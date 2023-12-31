import asyncio
import os
from fastapi import Query, Body, Depends
from fastapi.responses import StreamingResponse
from typing import Annotated, Union
from datetime import date
from src.utils.router import APIRouter
from src.infra.vda.vda_service import vdaService, MissionDataFileType
from src.resources.missions import mission_service
from src.core.mission.data import MissionVersionPolygon, UserIds, MissionImageAnnotation, MissionTilesetAnnotation, \
    MissionImagePolygon, MissionTilesetPolygon, MissionShare, ShareSendEmail
from src.core.user.data import UserCreateUpdate
from src.resources.dependency.dependencies import verify_auth_token, verify_role, unique_token, auth_dependency
from src.resources.roof_score.score_service import score_service
from src.utils.error.error import AppException

router = APIRouter(
    prefix="/mission",
    tags=["Mission"],
)


@router.get('', dependencies=[Depends(auth_dependency)])
async def get_missions(from_date: Annotated[Union[date, None], Query()] = None,
                       to_date: Annotated[Union[date, None], Query()] = None):
    missions = await vdaService.get_missions(from_date, to_date)
    return missions


@router.get('/{id}/missiondata', dependencies=[Depends(auth_dependency)])
async def get_mission_data(id: str):
    mission = await vdaService.get_mission_detail(id)
    return mission


@router.get('/{id}/datatype/{datatype}')
async def get_mission_data_files(id: str, datatype: str):
    if datatype == MissionDataFileType.demjpg:
        return await vdaService.get_mission_demjpg(id)
    elif datatype == MissionDataFileType.demtif:
        return await vdaService.get_mission_demtif(id)
    elif datatype == MissionDataFileType.demtile:
        return await vdaService.get_mission_demtile(id)
    elif datatype == MissionDataFileType.hdobj:
        return await vdaService.get_mission_hdobj(id)
    elif datatype == MissionDataFileType.geoobj:
        return await vdaService.get_mission_geoobj(id)
    elif datatype == MissionDataFileType.orthojpg:
        return await vdaService.get_mission_orthojpg(id)
    elif datatype == MissionDataFileType.orthotif:
        return await vdaService.get_mission_orthotif(id)
    elif datatype == MissionDataFileType.orthotile:
        return await vdaService.get_mission_orthotile(id)
    elif datatype == MissionDataFileType.tile3d:
        return await vdaService.get_mission_title3d(id)
    else:
        raise AppException(name='Invalid data type')


@router.get("/version/{version_id}/versionPolygons")
async def get_version_polygons(version_id: str):
    res = await mission_service.get_version_polygons(version_id)
    return res


@router.post("/version/{version_id}/versionPolygons", dependencies=[Depends(auth_dependency)])
async def add_version_polygons(version_id: str, data: MissionVersionPolygon):
    res = await mission_service.add_version_polygon(version_id, data)
    return res


@router.put("/version/{polygon_id}/versionPolygons", dependencies=[Depends(auth_dependency)])
async def update_version_polygons(polygon_id: str, data: MissionVersionPolygon):
    res = await mission_service.update_version_polygon(polygon_id, data)
    return res


@router.delete("/version/{polygon_id}/versionPolygons", dependencies=[Depends(auth_dependency)])
async def update_version_polygons(polygon_id: str):
    res = await mission_service.delete_version_polygon(polygon_id)
    return res


@router.get("/{version_id}/assignUsers")
async def get_version_assigned_user(version_id: str):
    res = await mission_service.get_version_assign_users(version_id)
    return res


@router.post("/{version_id}/assignUser", dependencies=[Depends(auth_dependency)])
async def edit_version_assigned_user(version_id: str, user=Depends(auth_dependency),
                                     data: UserIds = Body()):
    if data.add and len(data.add) > 0:
        await mission_service.add_version_assigned(user, version_id, data.add)
    if data.remove and len(data.remove) > 0:
        await mission_service.remove_version_assigned(user, version_id, data.remove)

    return {
        'success': 'true'
    }


@router.get("/{version_id}/mlImages")
async def get_ml_image_file(version_id: str):
    res = await mission_service.get_ml_image_file(version_id)
    return res


@router.get("/{version_id}/rawImages")
async def get_mission_raw_image(version_id: str):
    res = await vdaService.get_mission_raw_images(version_id)
    # check image processed by ML
    ml_images = await score_service.get_mission_version_images(version_id) or []
    for img in ml_images:
        raw_image = next((raw for raw in res if os.path.splitext(raw.get('title'))[0] == os.path.splitext(img.img_name)[0]),
                         None)
        if not raw_image:
            continue
        raw_image["mlProcessed"] = True
        if img.defects.polygons:
            raw_image["hasRoofDefects"] = True
    # TODO: update vda api to return this instead of client requesting each image
    # check image has annotations
    annotation_reqs = [vdaService.get_mission_image_annotation(r.get('_id') for r in res)]
    img_annotations = await asyncio.gather(*annotation_reqs)
    for a, idx in zip(img_annotations, range(len(res))):
        if a:
            res[idx]["hasAnnotations"] = True
    # check favourite images
    favourites = await mission_service.get_version_images_favourite(version_id)
    for f in favourites:
        raw = next((r for r in res if r["_id"] == f["imageId"]), None)
        if raw:
            raw["favourite"] = f["favourite"]
    return res


@router.put("/{version_id}/favourite/rawImages/{image_id}", dependencies=[Depends(auth_dependency)])
async def favourite_image(version_id: str, image_id: str):
    return await mission_service.favourite_image(version_id, image_id)


@router.get("/{versionId}/favourite/rawImages/{image_id}", dependencies=[Depends(auth_dependency)])
async def get_favourite_image(image_id: str):
    return await mission_service.get_image_favourite(image_id)


@router.get("/annotation/rawimage/{image_id}")
async def get_raw_image_annotation(image_id: str):
    res = await vdaService.get_mission_image_annotation(image_id)
    return res


@router.post("/annotation/rawimage/{image_id}", dependencies=[Depends(auth_dependency)])
async def create_raw_image_annotation(image_id: str, data: dict = Body()):
    res = await vdaService.create_mission_image_annotation(image_id, data)
    return res


@router.put("/annotation/rawimage/{image_id}", dependencies=[Depends(auth_dependency)])
async def update_raw_image_annotation(image_id: str, data: MissionImageAnnotation = Body()):
    res = await vdaService.update_mission_image_annotation(image_id, data.dict())
    return res


@router.delete("/annotation/rawimage/{image_id}", dependencies=[Depends(auth_dependency)])
async def delete_raw_image_annotation(image_id: str):
    res = await vdaService.delete_mission_image_annotation(image_id)
    return res


@router.get("/annotation/tileset/{version_id}")
async def get_titleset_annotation(version_id: str):
    res = await vdaService.get_mission_titleset_annotation(version_id)
    return res


@router.post("/annotation/tileset/{version_id}", dependencies=[Depends(auth_dependency)])
async def create_titleset_annotation(version_id: str, data: MissionTilesetAnnotation = Body()):
    res = await vdaService.create_titleset_annotation(version_id, data.dict())
    return res


@router.put("/annotation/tileset/{version_id}", dependencies=[Depends(auth_dependency)])
async def update_titleset_annotation(version_id: str, data: MissionTilesetAnnotation = Body()):
    res = await vdaService.update_titleset_annotation(version_id, data.dict())
    return res


@router.delete("/annotation/versionId/{version_id}", dependencies=[Depends(auth_dependency)])
async def delete_titleset_annotation(version_id: str):
    res = await vdaService.delete_titleset_annotation(version_id)
    return res


@router.get("/polygon/rawimage/{image_id}")
async def get_raw_image_polygon(image_id: str):
    res = await vdaService.get_mission_image_polygon(image_id)
    return res


@router.post("/polygon/rawimage/{image_id}", dependencies=[Depends(auth_dependency)])
async def create_raw_image_polygon(image_id: str, data: MissionImagePolygon = Body()):
    res = await vdaService.create_mission_image_polygon(image_id, data.dict())
    return res


@router.put("/polygon/rawimage/{image_id}", dependencies=[Depends(auth_dependency)])
async def update_raw_image_polygon(image_id: str, data: MissionImagePolygon = Body()):
    res = await vdaService.update_mission_image_polygon(image_id, data.dict())
    return res


@router.delete("/polygon/rawimage/{image_id}", dependencies=[Depends(auth_dependency)])
async def delete_raw_image_polygon(image_id: str):
    res = await vdaService.delete_mission_image_polygon(image_id)
    return res


@router.get("/polygon/tileset/{version_id}")
async def get_titleset_polygon(version_id: str):
    res = await vdaService.get_mission_titleset_polygon(version_id)
    return res


@router.post("/polygon/tileset/{version_id}", dependencies=[Depends(auth_dependency)])
async def create_titleset_polygon(version_id: str, data: MissionTilesetPolygon = Body()):
    res = await vdaService.create_mission_titleset_polygon(version_id, data.dict())
    return res


@router.put("/polygon/tileset/{version_id}", dependencies=[Depends(auth_dependency)])
async def update_titleset_polygon(version_id: str, data: MissionTilesetPolygon = Body()):
    res = await vdaService.update_mission_titleset_polygon(version_id, data.dict())
    return res


@router.delete("/polygon/versionId/{version_id}", dependencies=[Depends(auth_dependency)])
async def delete_titleset_polygon(version_id: str):
    res = await vdaService.delete_mission_titleset_polygon(version_id)
    return res


@router.post("/share", dependencies=[Depends(auth_dependency)])
async def create_mission_share(user: dict = Depends(verify_auth_token), data: MissionShare = Body()):
    res = await mission_service.create_share(data.dict(), user)
    return res


@router.post("/share-send-by-email", dependencies=[Depends(auth_dependency)])
async def share_by_email(user: dict = Depends(verify_auth_token), data: ShareSendEmail = Body()):
    await mission_service.share_send_mail(data.dict(), user)


@router.get("/share/{share_id}")
async def get_share_by_id(share_id: str):
    return await mission_service.get_share(share_id)


@router.get("/share/{share_id}/info")
async def get_share_info(share_id: str):
    return await mission_service.get_share_info(share_id)


@router.get("/version/{version_id}/share")
async def get_version_share(version_id: str):
    return await mission_service.get_share_by_version(version_id)


@router.post("/version/{version_id}/submit-emc", dependencies=[Depends(auth_dependency)])
async def submit_version_to_emc(version_id: str):
    return await mission_service.submit_mission_version_to_emc(version_id)


@router.get("/version/{version_id}/downloadFiles", dependencies=[Depends(auth_dependency)])
async def get_version_download_files(version_id: str):
    return await mission_service.get_mission_version_download_files(version_id)


@router.get("/resize", dependencies=[Depends(auth_dependency)])
async def get_resize_image(s3: str, key: str, size: int):
    file = await vdaService.get_resize_image(s3, key, size)

    def iterfile():  #
        with file as file_like:  #
            yield from file_like

    return StreamingResponse(iterfile(), media_type='image/jpeg')


@router.get("/presign/{url}", dependencies=[Depends(auth_dependency)])
async def get_presign_url(url: str):
    file = await vdaService.get_presign(url)

    def iterfile():  #
        with file as file_like:  #
            yield from file_like

    return StreamingResponse(iterfile(), media_type='image/jpeg')


@router.get("/share/{share_id}/resize")
async def get_share_resize_image(share_id: str, s3: str, key: str, size: int):
    share_info = await mission_service.get_share_info(share_id)
    if share_info:
        file = await vdaService.get_resize_image(s3, key, size)

        def iterfile():  #
            with file as file_like:  #
                yield from file_like

        return StreamingResponse(iterfile(), media_type='image/jpeg')
    else:
        raise AppException(name='Not found')


@router.get("/share/{share_id}/presign/{url}")
async def get_share_presign_url(share_id: str, url: str):
    share_info = await mission_service.get_share_info(share_id)
    if share_info:
        file = await vdaService.get_presign(url)

        def iterfile():  #
            with file as file_like:  #
                yield from file_like

        return StreamingResponse(iterfile(), media_type='image/jpeg')
    else:
        raise AppException(name='Not found')
