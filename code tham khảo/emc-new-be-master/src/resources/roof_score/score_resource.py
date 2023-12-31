import asyncio
from fastapi import Body, Depends, BackgroundTasks
from src.utils.router import APIRouter
from src.infra.vda.vda_service import vdaService
from src.resources.roof_score.score_service import score_service
from src.resources.missions.mission_service import update_mission_version_csv_data
from src.core.roof_score.data import MissionScoreCreate, MissionImageCreate, MissionScoreUpdatePayload, MissionScore,MissionUpdateScoreStatus
from src.resources.dependency.dependencies import auth_dependency
from src.worker import update_mission_score, get_celery_task_status
from src.infra.database import get_mission_score_collection, get_mission_update_score_status



router = APIRouter(
    prefix="/score",
    tags=["Score"],
)

@router.get("/complete-status-notification", dependencies=[Depends(auth_dependency)])
async def get_version_complete_status_notification(current_user = Depends(auth_dependency)):
    collection = get_mission_update_score_status()
    cursor = collection.find({
        'user_id': current_user.get('_id'), 
        "update_status": { "$in": ['SUCCESS', 'FAILURE']},
    })

    tasks = []
    res = []
    for s in await cursor.to_list(None):
        # get mission data
        async def get_mission_data_task(status_obj):
            # objectId not serializable
            status_obj.pop('_id')
            # get version data
            data = await vdaService.get_mission_detail(status_obj.get('version_id'))
            status_obj['mission_data'] = data

            res.append(status_obj)
        tasks.append(get_mission_data_task(s))

    await asyncio.gather(*tasks)
    
    return res

@router.post("/set-notification", dependencies=[Depends(auth_dependency)])
async def set_notification_version_update_status(version_ids: list, current_user = Depends(auth_dependency)):
    collection = get_mission_update_score_status()
    await collection.delete_many({
        'version_id':  {'$in': version_ids},
        'user_id': current_user.get('_id'),
    })
    return True

@router.get("/{version_id}")
async def get_mission_version_score(version_id: str, need_updates: bool = True):
    score = await score_service.get_mission_version_score(version_id, need_updates)

    return score


@router.get("/{version_id}/image")
async def get_mission_version_images(version_id: str, is_filter_threshold: bool):
    score = await score_service.get_mission_version_images(version_id, is_filter_threshold)
    return score


@router.get("/{version_id}/image/{img_name}")
async def get_mission_version_image_score(version_id: str, img_name: str):
    score = await score_service.get_mission_version_image_by_name(version_id, img_name)
    return score


@router.post("", dependencies=[Depends(auth_dependency)])
async def create_mission_version(data: MissionScoreCreate):
    res = await score_service.create_misison_version_score(data)
    return res


@router.post("/{version_id}/image", dependencies=[Depends(auth_dependency)])
async def create_mission_version_image(version_id: str, data: MissionImageCreate):
    res = await score_service.create_misison_version_image_score(version_id, data)
    return res


async def update_csv_file(version_id: str):
    try:
        version_score = await score_service.get_mission_version_score(version_id)
        if not version_score:
            raise Exception("Mission data not available for submit")
        emc_rcif = version_score.emc_rcif
        data_prefix = f"{emc_rcif}/{version_id}"
        await update_mission_version_csv_data(emc_rcif, data_prefix, version_id)
    except Exception as e:
        print('[update_csv_file error]:', e)


@router.post("/{version_id}/score-update", dependencies=[Depends(auth_dependency)])
async def update_mission_version_defects(version_id: str, data: MissionScoreUpdatePayload,
                                         background_tasks: BackgroundTasks, current_user = Depends(auth_dependency)):
    document = await score_service.get_mission_version_score(version_id)
    # Check score update with status
    if document.task_updating is not None:
        return {
            'error': 'Mission score is updating'
        }
    if not document:
        return {
            'error': 'Version id does not exist'
        }
    # create task to run update_mission_score
    task = update_mission_score.delay(version_id, data.dict(), current_user.get('email'), current_user.get('_id'))

    # create or update mission_updated_score_status when starting task
    mission_updated_score_status = get_mission_update_score_status()
    await mission_updated_score_status.update_one({
        'version_id': version_id
    }, {
        '$set': {
            'user_id': current_user.get('_id'),
            'update_status': task.status
        }
    },
        upsert=True
    )

    collection = get_mission_score_collection()
    await collection.update_one({
        'mission_id': version_id
    }, {
        '$set': {'task_updating': task.id}
    })
    return {"task_id": task.id}


@router.post("/{version_id}/revert-score", dependencies=[Depends(auth_dependency)])
async def revert_mission_version_score(version_id: str):
    res = await score_service.revert_mission_version_score(version_id)
    return res
