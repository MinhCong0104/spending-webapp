
import asyncio
from pathlib import Path
from typing import Union

from src.utils.router import APIRouter
from src.infra.database import get_mission_images_collection, get_mission_score_collection
from src.core.roof_score.data import MissionImageCreate, MissionScoreCreate, MissionScore, MissionImage, Defect, MissionScoreUpdatePayload
from src.core.roof_score.calculation import calculate_roof_score_updates, filter_defect_by_threshold, handle_unprocessed_images
from src.utils.date import getNowUTCTime
from src.core.roof_score.image import redraw_mission_images, update_image_list

router = APIRouter(
    prefix="/roof-score",
    tags=["roof score"],
)

@router.get('/{mission_id}/', response_model=MissionScore)
async def get_mission_score(mission_id: str, need_updates: bool):
    collection = get_mission_score_collection()
    
    projection = { 'updates': 0 }

    if need_updates:
        document = await collection.find_one({ 'mission_id': mission_id })
    else:
        document = await collection.find_one({ 'mission_id': mission_id }, projection)

    if not document:
        return None

    return MissionScore.parse_obj(document)

@router.post('')
async def create_mission_score(data: MissionScoreCreate):
    collection = get_mission_score_collection()

    document = await collection.find_one({ 'mission_id': data.mission_id })

    if document:
        return {
            'error': 'Mission id already exist'
        }

    new_mission_score = {
        'mission_id': data.mission_id,
        'avg_score': data.avg_score,
        'emc_rcif': data.emc_rcif,
    }

    await collection.insert_one(new_mission_score)

    return {
        'success': True
    }

@router.get('/{mission_id}/image', response_model=list[MissionImage])
async def get_mission_images(mission_id: str, is_original: Union[bool, None] = None, is_filter_threshold: Union[bool, None] = None):
    collection = get_mission_score_collection()

    document = await collection.find_one({ 'mission_id': mission_id })

    if not document:
        return {
            'error': 'Mission id does not exist'
        }


    collection = get_mission_images_collection()
    # not returning defects points and roof_mask in list image api to reduce memory usage
    cursor = collection.find({ 'mission_id': mission_id }, { 'defects.polygons.points': 0, 'roof_mask': 0, 'env_contours': 0 })

    images = [MissionImage.parse_obj(d) for d in await cursor.to_list(None)]
    if is_original:
        return images

    mission_score = MissionScore.parse_obj(document)
    if len(mission_score.updates) < 1:
        return images

    # use latest image update value for returned images list
    update_image_list(images, mission_score.updates)

    latest_update = mission_score.updates[len(mission_score.updates) - 1]
    # filter image defect by threshold if request
    if is_filter_threshold:
        for img in images:
            # use image specific threshold or project threshold
            threshold_settings = img.threshold_settings or latest_update.project_threshold_settings
            if threshold_settings:
                # filter defect by threshold if has threshold settings
                defect_polygons = [d for d in img.defects.polygons if filter_defect_by_threshold(d, threshold_settings)] if threshold_settings else img.defects.polygons
                if not img.defects:
                    img.defects = Defect(polygons=defect_polygons)
                else:
                    img.defects.polygons = defect_polygons

    return images

@router.get('/{mission_id}/image/{img_name}', response_model=MissionImage)
async def get_mission_image_by_name(mission_id: str, img_name: str):
    collection = get_mission_images_collection()
    file_name = Path(img_name).stem
    document = await collection.find_one({ 'mission_id': mission_id, 'img_name': { '$regex': file_name } })
    if not document:
        return None

    return MissionImage.parse_obj(document)

@router.post('/{mission_id}/image')
async def create_mission_image_data(mission_id: str, data: MissionImageCreate):
    # TODO: might need to check mission score doc exist
    # mission_score_collection = get_mission_score_collection()
    # document = await mission_score_collection.find_one({ 'mission_id': mission_id })

    # if not document:
    #     return {
    #         'error': 'Mission id does not exist'
    #     }
    mission_id = data.mission_id or mission_id

    mission_image_collection = get_mission_images_collection()
    document = await mission_image_collection.find_one({ 'mission_id': mission_id, 'img_name': data.img_name })

    new_mission_image = {
        'mission_id': mission_id,
        **data.dict(exclude_none=True)
    }

    # update document if already exist
    # else create new
    if document:
        await mission_image_collection.update_one({ 'mission_id': mission_id, 'img_name': data.img_name }, {
            '$set': new_mission_image
        })
    else:
        await mission_image_collection.insert_one(new_mission_image)

    return {
        'success': True
    }

@router.post('/{mission_id}/update-images-to-emc')
async def update_images_to_emc(mission_id: str):
    mission_score_collection = get_mission_score_collection()
    document = await mission_score_collection.find_one({ 'mission_id': mission_id })
    if not document:
        return {
            'error': 'Mission id does not exist'
        }
    mission_score = MissionScore.parse_obj(document)

    mission_image_collection = get_mission_images_collection()

    cursor = mission_image_collection.find({ 'mission_id': mission_id })
    mission_images = [MissionImage.parse_obj(d) for d in await cursor.to_list(None)]

    project_threshold_settings = mission_score.project_threshold_settings
    if len(mission_score.updates) >= 1:
        latest_update = mission_score.updates[len(mission_score.updates) - 1]

        # use latest image update value for returned images list
        update_image_list(mission_images, mission_score.updates)
        project_threshold_settings = latest_update.project_threshold_settings

    redraw_mission_images(mission_images, project_threshold_settings)

@router.post('/{mission_id}/mission-score-update')
async def update_mission_score_image(mission_id: str, update: MissionScoreUpdatePayload):
    mission_score_collection = get_mission_score_collection()
    document = await mission_score_collection.find_one({ 'mission_id': mission_id })
    if not document:
        return {
            'error': 'Mission id does not exist'
        }

    if not update.project_threshold_settings and not update.image_updates:
        return {
            'error': 'Invalid update'
        }

    initial_mission_score = MissionScore.parse_obj(document)

    mission_image_collection = get_mission_images_collection()

    projection = { 'defects': 0 } # no need defects in this calculation so we can prevent fetching those and reduce memory consume ( defects polygons from ML size are huge atm )
    if update.project_threshold_settings:
        projection = None # get defects data to recalculate all images when project threshold change
    cursor = mission_image_collection.find({ 'mission_id': mission_id }, projection)
    mission_images = [MissionImage.parse_obj(d) for d in await cursor.to_list(None)]
    
    handle_unprocessed_images(mission_images, update, initial_mission_score.emc_rcif, initial_mission_score.mission_id)
    # reload mission_images list after unprocessed images added
    cursor = mission_image_collection.find({ 'mission_id': mission_id }, projection)
    mission_images = [MissionImage.parse_obj(d) for d in await cursor.to_list(None)]
    # update image_list with latest previous updates
    update_image_list(mission_images, initial_mission_score.updates)
    # calculate new score
    new_avg_score, image_update_scores = calculate_roof_score_updates(mission_images, update, initial_mission_score.emc_rcif, initial_mission_score.mission_id)

    # update new score to db
    new_score_update = {
        'image_updates': [
            {
                **img_update.dict(exclude_none=True),
                'score': image_update_scores[index]
            } for index, img_update in enumerate(update.image_updates)
        ],
        'avg_score': new_avg_score,
        'time': getNowUTCTime()
    }
    if update.project_threshold_settings:
        new_score_update['project_threshold_settings'] = update.project_threshold_settings.dict(exclude_none=True)
    await mission_score_collection.update_one({
        '_id': initial_mission_score.id
    }, {
        '$push': { 'updates': new_score_update }
    })

    return {
        'success': True,
        'new_avg_score': new_avg_score
    }

@router.post('/{mission_id}/revert_score',)
async def revert_mission_score(mission_id: str):
    mission_score_collection = get_mission_score_collection()
    document = await mission_score_collection.find_one({ 'mission_id': mission_id })
    if not document:
        return {
            'error': 'Mission id does not exist'
        }

    mission_score = MissionScore.parse_obj(document)
    if len(mission_score.updates) < 1:
        return {
            'error': 'No mission score updated yet'
        }

    await mission_score_collection.update_one({
        '_id': mission_score.id
    }, {
        '$set': {
            'updates': []
        }
    })

    return {
        'success': True
    }

@router.post('/{mission_id}/submit_score',)
async def submit_mission_score(mission_id: str):
    mission_score_collection = get_mission_score_collection()
    document = await mission_score_collection.find_one({ 'mission_id': mission_id })
    if not document:
        return {
            'error': 'Mission id does not exist'
        }

    mission_score = MissionScore.parse_obj(document)
    await mission_score_collection.update_one({
        '_id': mission_score.id
    }, {
        '$set': {
            'submitted_date': getNowUTCTime(),
        }
    })

    return {
        'success': True
    }
