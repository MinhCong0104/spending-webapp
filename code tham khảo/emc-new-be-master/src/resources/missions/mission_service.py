import asyncio
import os
import typing
import tempfile
import csv
from datetime import datetime, timedelta, date
from bson import ObjectId
from src.config.settings import settings
from src.core.mission.data import MissionVersionPolygon, MissionVersionPolygonUpdate, MissionVersion, \
    MissionRawImageFavourite, MissionShare
from src.core.user.data import UserCreateUpdate

from src.infra.database import get_version_polygon_collection, get_mission_version_assign_collection, \
    get_mission_raw_image_favourite, get_mission_share
from src.infra.mail.storage_service import storage_service
from src.infra.vda.vda_service import vdaService
from src.resources.roof_score.score_service import score_service
from src.resources.user.user_service import user_service
from src.infra.mail.mail_service import mail_service
from src.infra.mail.queue_service import queue_service
from src.infra.mail.template import email_template, header, sub_header
from src.infra.secret.secret_service import secret_service
from src.core.user.data import VDAUserRole
from src.core.roof_score.data import DefectClass
from src.utils.error.error import AppException


async def get_version_polygons(version_id: str):
    version = await vdaService.get_mission_detail(version_id)
    if not version:
        raise AppException(name='Invalid version!')
    collection = get_version_polygon_collection()
    version_polygon = await collection.find_one({'versionId': version_id})
    if not version_polygon:
        return None
    return MissionVersionPolygon.parse_obj(version_polygon)


async def add_version_polygon(version_id: str, data: MissionVersionPolygon):
    version = await vdaService.get_mission_detail(version_id)
    if not version:
        raise AppException(name='Invalid version!')
    collection = get_version_polygon_collection()
    version_polygon = await collection.find_one({'versionId': version_id})
    if version_polygon:
        return {
            'error': 'Version id already exist'
        }
    collection.insert_one(data.dict())
    return {
        'success': True
    }


async def update_version_polygon(polygon_id: str, data: MissionVersionPolygonUpdate):
    collection = get_version_polygon_collection()
    version_polygon = await collection.find_one({'versionId': polygon_id})
    if not version_polygon:
        return {
            'error': 'Invalid Polygon Id'
        }
    collection.update_one({
        'versionId': polygon_id
    }, {
        '$set': data.dict()
    })
    return {
        'updated_data': data
    }


async def delete_version_polygon(polygon_id: str):
    collection = get_version_polygon_collection()
    version_polygon = await collection.find_one({'versionId': polygon_id})
    if not version_polygon:
        return {
            'error': 'Invalid Polygon Id'
        }
    collection.delete_one({"_id": version_polygon.get('_id')})
    return {
        'success': True
    }


async def get_version_assign_users(version_id: str, includeDefaultUsers: typing.Union[bool, str] = True):
    collection = get_mission_version_assign_collection()
    assign = await collection.find_one({'versionId': version_id})
    assigned_ids = []
    if assign:
        assigned_ids = assign.get('users', [])
    if includeDefaultUsers:
        version = await vdaService.get_mission_detail(version_id)
        if not version:
            raise AppException(name='Invalid version!')
        company_users = await user_service.get_all_company_user()
        for company_user in company_users:
            if company_user.get('role') in [VDAUserRole.Admin, VDAUserRole.SuperAdmin] or \
                    company_user.get('_id') == version.get('pilot', {}).get('_id'):
                assigned_ids.append(company_user.get('_id'))

    assigned_users = [vdaService.getUserDetail(assigned_id) for assigned_id in assigned_ids]
    res = await asyncio.gather(*assigned_users)
    res = [assigned_user for assigned_user in res if not assigned_user.get('message')]
    return res


async def add_version_assigned(user: UserCreateUpdate, version_id: str, user_ids: list):
    version = await vdaService.get_mission_detail(version_id)
    is_user_allowed_update = await validate_user_assign(user, version)
    if not is_user_allowed_update:
        raise AppException(name='User does not have permission')

    collection = get_mission_version_assign_collection()
    await collection.update_one({
        'versionId': version_id
    }, {
        '$addToSet': {
            'users': {
                '$each': user_ids
            }
        }
    },
        upsert=True
    )

async def remove_version_assigned(user: UserCreateUpdate, version_id: str, user_ids: list):
    version = await vdaService.get_mission_detail(version_id)
    if not version:
        raise AppException(name='Invalid version!')
    is_user_allowed_update = await validate_user_assign(user, version)
    if not is_user_allowed_update:
        raise AppException(name='User does not have permission')

    if version.get('pilot') and version.get('pilot').get('_id') in user_ids:
        raise AppException(name='Can not remove creator assign')

    collection = get_mission_version_assign_collection()
    await collection.update_one({
        'versionId': version_id
    }, {
        '$pullAll': {
            'users': user_ids
        }
    })


async def validate_user_assign(user: UserCreateUpdate, version: MissionVersion):
    user_allowed_update = True if user.get('role') in [VDAUserRole.Admin, VDAUserRole.SuperAdmin] \
                                  or user.get('_id') == version.get('pilot').get('_id') else False

    return user_allowed_update


async def get_ml_image_file(version_id: str):
    ml_images = await score_service.get_mission_version_images(version_id)
    reqs = []
    for img in ml_images:
        reqs.append(loop_ml_images(img, version_id))
    return await asyncio.gather(*reqs)


async def loop_ml_images(img, version_id):
    bucket = settings.report_s3
    file_name = os.path.splitext(img.img_name)[0]
    # get download url for ml images and csv
    img_base_path = f'{img.emc_rcif}/{version_id}/structure1/hdimages'
    filtered_file = f'{img_base_path}/{file_name}_filtered.jpg'
    masking_file = f'{img_base_path}/{file_name}_masking.jpg'
    roof_file = f'{img_base_path}/{file_name}_roof.jpg'

    csv_base_path = f'{img.emc_rcif}/{version_id}/structure1/extras/CSV'
    filrtered_csv_file = f'{csv_base_path}/{file_name}_filtered.csv'
    masking_csv_file = f'{csv_base_path}/{file_name}_masking.csv'

    filtered_img_url = storage_service.get_file_url({'bucket': bucket, 'key': filtered_file})
    masking_img_url = storage_service.get_file_url({'bucket': bucket, 'key': masking_file})
    roof_img_url = storage_service.get_file_url({'bucket': bucket, 'key': roof_file})
    filtered_csv_file_url = storage_service.get_file_url({'bucket': bucket, 'key': filrtered_csv_file})
    masking_csv_file_url = storage_service.get_file_url({'bucket': bucket, 'key': masking_csv_file})

    image_urls = await asyncio.gather(filtered_img_url, masking_img_url, roof_img_url, filtered_csv_file_url,
                                      masking_csv_file_url)
    image_urls = [img.img_name, img.score, image_urls]
    return image_urls


async def get_version_images_favourite(version_id: str):
    collection = get_mission_raw_image_favourite()
    cursor = collection.find({'versionId': version_id})
    return await cursor.to_list(None)


async def favourite_image(version_id: str, image_id: str):
    collection = get_mission_raw_image_favourite()
    raw_image_favourite = await collection.find_one({'versionId': version_id, 'imageId': image_id})
    version_data = await vdaService.get_mission_detail(version_id)
    if not version_data:
        raise AppException(name='Invalid version data!')

    # TODO: validate image id
    if not raw_image_favourite:
        new_raw_image_favourite = {
            'versionId': version_id,
            'imageId': image_id,
            'favourite': True
        }
        await collection.insert_one(new_raw_image_favourite)
        return
    await collection.update_one(
        {'_id': raw_image_favourite.get('_id')},
        {
            '$set': {
                'favourite': True if not raw_image_favourite.get('favourite') else False,
            }
        }
    )


async def get_image_favourite(image_id: str):
    collection = get_mission_raw_image_favourite()
    raw_image_favourite = await collection.find_one({'imageId': image_id})
    if not raw_image_favourite:
        return None
    return MissionRawImageFavourite.parse_obj(raw_image_favourite)


async def create_share(data: dict, user: dict):
    creator_id = data.get('creator') or user.get('_id')
    if not creator_id:
        raise AppException(name='Creator required')
    creator = await vdaService.getUserDetail(creator_id)
    if not creator:
        raise AppException(name='Invalid creator!')
    version_data = await vdaService.get_mission_detail(data.get('versionId'))
    if not version_data:
        raise AppException(name='Invalid version data!')

    # share expire in 7 days
    default_exp = datetime.now()
    default_exp = default_exp + timedelta(days=7)
    exp = data.get('exp')
    # if data.get('exp') and exp > default_exp:
    if data.get('exp'):
        default_exp = exp

    collection = get_mission_share()
    new_mission_share = {
        **data,
        "creator": creator_id,
        "exp": default_exp
    }
    res = await collection.insert_one(new_mission_share)
    return {
        **new_mission_share,
        '_id': str(res.inserted_id)
    }


async def share_send_mail(data: dict, user: dict):
    collection = get_mission_share()
    share = await collection.find_one({'_id': ObjectId(data.get('shareId'))})
    if not share:
        raise AppException(name='Invalid version id')

    version_data = await vdaService.get_mission_detail(share.get('versionId'))
    if not version_data:
        raise AppException(name='Invalid version id')
    mission_score = await score_service.get_mission_version_score(share.get('versionId'))
    # latest_update = mission_score.updates[len(mission_score.updates) - 1] if len(mission_score.updates) > 1 else None
    if mission_score:
        latest_update = mission_score.updates[-1] if len(mission_score.updates) > 1 else None
        latest_score = (latest_update.avg_score if latest_update else mission_score.avg_score)
    else:
        latest_score = 0


    mail_body = share_mission_html(
        f"EMC location {version_data.get('missionname')} {'report data' if share.get('onlyReport') else 'mission data'} shared by "
        f"{user.get('firstName') or ''} {user.get('lastName') or ''}. <br>The score for mission "
        f"{version_data.get('missionname')} is {latest_score:.2f}",
        f"Please click the link here <a href='{data.get('url')}'>{data.get('url')}</a> to view the {'report data' if share.get('onlyReport') else 'mission data'} for {version_data.get('missionname')}")

    subject = f"EMC location {version_data.get('missionname')} {'report data' if share.get('onlyReport') else 'mission data'} shared by {user.get('firstName') or ''} {user.get('lastName') or ''}"
    await mail_service.send_mail(data.get('email'), email_template.EmailTemplate(mail_body), subject)
    await collection.update_one({
        '_id': share.get('_id')
    }, {
        '$set': {'email': data.get('email')}
    })


def share_mission_html(h, s):
    return f"""
        {header.Header(h)}
        {sub_header.SubHeader(s)}
    """


async def get_share_initialize_keys():
    google_map_secret = secret_service.get_secret(settings.google_maps_secret_name)
    return {
        'key': google_map_secret.get('Key')
    }


async def get_share(share_id: str):
    collection = get_mission_share()
    share = await collection.find_one({'_id': ObjectId(share_id)})
    share = MissionShare.parse_obj(share)
    if not share:
        return None
    if share.exp < datetime.now():
        raise AppException(name='Share expired')
    version_data = await vdaService.get_mission_detail(share.versionId)
    if not version_data:
        raise AppException(name='Invalid version data!')
    key = await get_share_initialize_keys()
    return {
        "Keys": key,
        "share": share,
        "version": version_data
    }


async def get_share_info(share_id: str):
    collection = get_mission_share()
    share = await collection.find_one({'_id': ObjectId(share_id)})
    if not share:
        return None
    if share.get('exp') < datetime.now():
        raise AppException('Share expired')
    return MissionShare.parse_obj(share)


async def get_share_by_version(version_id: str):
    collection = get_mission_share()
    share = await collection.find_one({'versionId': version_id})
    if not share:
        return None
    return MissionShare.parse_obj(share)


async def submit_mission_version_to_emc(version_id: str):
    await score_service.submit_mission_version_score(version_id)
    try:
        await send_mission_version_data_to_emc(version_id)
    except Exception as e:
        print('[submit_mission_version_to_emc error]:', e)


async def send_mission_version_data_to_emc(version_id: str):
    version_score = await score_service.get_mission_version_score(version_id)
    if not version_score:
        raise AppException(name='Mission data not available for submit')

    emc_rcif = version_score.emc_rcif
    data_prefix = f'{emc_rcif}/{version_id}'
    emc_resource_secret = secret_service.get_secret(settings.emc_owned_resources_secret_name)
    emc_s3 = emc_resource_secret.get('S3')
    emc_queue_url = emc_resource_secret.get('SQS_URL')
    await copy_mission_version_data_to_emc(emc_rcif, data_prefix, emc_s3, version_id)
    await send_data_message_to_emc(version_score.emc_rcif, emc_queue_url)


async def send_data_message_to_emc(data_prefix: str, queue: str):
    try:
        await queue_service.send_message(data_prefix, queue)
    except Exception as e:
        print('[send_data_message_to_emc error]:', e)
        raise e


async def copy_mission_version_data_to_emc(emc_rcif: str, data_prefix: str, destination_bucket: str, version_id: str):
    try:
        await update_mission_version_csv_data(emc_rcif, data_prefix, version_id)
        # copy csv all file to emc owned s3
        await copy_csv_data_to_emc(emc_rcif, data_prefix, destination_bucket)
        # redraw all images with updated defects
        await score_service.update_images_to_emc(version_id)

        # copy redrawn images to emc s3
        destination_root = f"{emc_rcif}/filtered_output"
        ml_images_prefix = f"{data_prefix}/structure1/hdimages_updated"
        ml_image_files = await storage_service.list_files(settings.report_s3, ml_images_prefix)
        filtered_ml_image_keys = [c for c in ml_image_files.get('Contents') if c.get('Key')]
        copy_tasks = []
        for key in filtered_ml_image_keys:
            async def copy_task(key):
                name, ext = os.path.splitext(key['Key'])
                image_file_name = f"{name}{ext}"
                destination_image_path = f"{destination_root}/images/{image_file_name}"
                await storage_service.copy_file(settings.report_s3, key['Key'], destination_bucket, destination_image_path)
            copy_tasks.append(copy_task(key))
        await asyncio.gather(*copy_tasks)
    except Exception as e:
        print('[copyMissionVersionDataToEMC error]:', e)
        raise e


async def copy_csv_data_to_emc(emc_rcif: str, data_prefix: str, destination_bucket: str):
    destination_root = f"{emc_rcif}/filtered_output"

    updated_csv_file_path = f"{data_prefix}/structure1/extras/CSV_all/{emc_rcif}_updated.csv"
    updated_ccore_csv_file_path = f"{data_prefix}/structure1/extras/CSV_all/{emc_rcif}_score_updated.csv"

    # copy files to emc s3
    destination_csv_file_path = f"{destination_root}/csv/{emc_rcif}.csv"
    await storage_service.copy_file(settings.report_s3, updated_csv_file_path,
                                    destination_bucket, destination_csv_file_path)

    destination_score_csv_file_path = f"{destination_root}/csv/{emc_rcif}_score.csv"
    await storage_service.copy_file(settings.report_s3, updated_ccore_csv_file_path,
                                    destination_bucket, destination_score_csv_file_path)


async def update_mission_version_csv_data(emc_rcif: str, data_prefix: str, version_id: str):
    # get latest image data and defect from score service with defect threshold filtered
    image_score = await score_service.get_mission_version_images(version_id, None, True)
    # create new updated csv with updated defect in each image
    updated_defect_csv_records = []
    for curr in image_score:
        new_image_defect_list = []
        # only push unique defect class to image
        for p in curr.defects.polygons:
            reformated_defect = to_formated_defect(p.defect_class)
            defect_exist = any(i['defect'] == reformated_defect for i in new_image_defect_list)
            if not defect_exist:
                new_image_defect_list.append({
                    'image': curr.img_name,
                    'defect': reformated_defect
                })
        updated_defect_csv_records.extend(new_image_defect_list)

    with tempfile.SpooledTemporaryFile(mode='w') as file:
        updated_defect_csv_string = csv.DictWriter(file, fieldnames=['image', 'defect'])
        updated_defect_csv_string.writeheader()
        updated_defect_csv_string.writerows(updated_defect_csv_records)
        file.seek(0)
        updated_csv_file_path = f"{data_prefix}/structure1/extras/CSV_all/{emc_rcif}_updated.csv"
        await storage_service.put_file(file.read().encode('utf-8'), {
            'key': updated_csv_file_path,
            'bucket': settings.report_s3
        })

    # create score csv with overall score and each image score
    version_score = await score_service.get_mission_version_score(version_id)
    # use latest update score if possible
    latest_update = version_score.updates[len(version_score.updates) - 1] if len(version_score.updates) > 0 else None
    latest_acc_score = latest_update.avg_score if latest_update else version_score.avg_score
    updated_score_csv_records = [
        {
            'image': 'avg_score',
            'score': latest_acc_score
        }
    ]

    for curr in image_score:
        curr_image_name = os.path.splitext(curr.img_name)[0]
        # use latest updated image score if present
        image_in_update = None
        if latest_update:
            image_in_update = next(
                (iu for iu in latest_update.image_updates if os.path.splitext(iu.img_name)[0] == curr_image_name),
                None)
        else:
            None
        image = image_in_update if image_in_update else curr
        defect_nums = len(image.defects.polygons) if image and image.defects and image.defects.polygons else 0
        updated_score_csv_records.append({
            'image': curr.img_name,
            'score': image.score if defect_nums > 0 else 1
        })

    with tempfile.SpooledTemporaryFile(mode='w') as file:
        updated_score_csv_string = csv.DictWriter(file, fieldnames=['image', 'score'])
        updated_score_csv_string.writeheader()
        updated_score_csv_string.writerows(updated_score_csv_records)
        file.seek(0)
        updated_score_csv_file_path = f"{data_prefix}/structure1/extras/CSV_all/{emc_rcif}_score_updated.csv"
        await storage_service.put_file(file.read().encode('utf-8'), {
            "key": updated_score_csv_file_path,
            "bucket": settings.report_s3
        })


def to_formated_defect(defect_class: DefectClass):
    reformat = {
        defect_class.Background: 'Background',
        defect_class.Ponding: 'Ponding',
        defect_class.BallastDisplacement: 'BallastDisplacement',
        defect_class.RoofMold: 'RoofMold',
        defect_class.Corrosion: 'Corrosion',
        defect_class.WrinkledMembrane: 'WrinkledMembrane',
        defect_class.WalkwayCrack: 'WalkwayCrack',
        defect_class.Patching: 'Patching',
        defect_class.Debris: 'Debris',
        defect_class.LowStepContrast: 'LowStepContrast',
        defect_class.OverhangingVegetation: 'OverhangingVegetation',
        defect_class.BLockedDrain: 'BlockedDrain',
        defect_class.DamagedWalkways: 'DamagedWalkways',
        defect_class.StepsWithoutAdequateContrast: 'StepsWithoutAdequateContrast'
    }
    return reformat[defect_class]


async def get_mission_version_download_files(version_id: str):
    version_score = await score_service.get_mission_version_score(version_id)
    if not version_score:
        return None
    version_path = f"{version_score.emc_rcif}/{version_id}"
    zip_files_prefix = f"{version_path}/structure1/extras/zipfiles"
    orthor_zip_file_name = "ortho.zip"
    hd_images_zip_file_name = "hdimages.zip"
    ml_images_zip_file_name = "mlimages.zip"
    csv_zip_file_name = "csv.zip"

    orthor_link = get_zip_file_url(zip_files_prefix, orthor_zip_file_name)
    hd_images_link = get_zip_file_url(zip_files_prefix, hd_images_zip_file_name)
    ml_images_link = get_zip_file_url(zip_files_prefix, ml_images_zip_file_name)
    csv_link = get_zip_file_url(zip_files_prefix, csv_zip_file_name)

    orthor_link, hd_images_link, ml_images_link, csv_link = await asyncio.gather(orthor_link, hd_images_link, ml_images_link, csv_link)
    return {
        "orthoLink": orthor_link,
        "hdImagesLink": hd_images_link,
        "mlImagesLink": ml_images_link,
        "csvLink": csv_link
    }

async def get_zip_file_url(prefix: str, file_name: str):
    return await storage_service.get_file_url({
        "bucket": settings.report_s3,
        "key": f"{prefix}/{file_name}"
    })