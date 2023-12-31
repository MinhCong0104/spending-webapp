import os
from celery import Celery
from celery.result import AsyncResult
from src.resources.missions.mission_service import update_mission_version_csv_data
from src.resources.roof_score.score_service import score_service
from src.core.roof_score.data import MissionScoreUpdatePayload
import asyncio
import functools
from src.infra.database import connect_db, close_db, get_mission_score_collection, get_mission_update_score_status
from src.infra.vda.vda_service import vdaService
from src.infra.mail.mail_service import mail_service
from src.infra.mail.template import email_template, header, sub_header
from src.config.settings import settings

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(__name__)
celery_app.conf.broker_url = REDIS_URL
celery_app.conf.result_backend = REDIS_URL
celery_app.conf.task_track_started = True
celery_app.conf.task_ignore_result = False

# print(celery_app.conf)

def sync(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        connect_db()
        try:
            return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))
        finally:
            close_db()
    return wrapper


# @celery_app.task(name="run_task")
# def run_celery_task() -> str:
#     return execute()
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


@celery_app.task(name="update_mission_score")
@sync
async def update_mission_score(version_id, data, user_email, user_id):
    # data send through celery is serialized to dict
    # convert back to pydantic object
    try:
        update_data = MissionScoreUpdatePayload.parse_obj(data)
        await score_service.update_mission_version_defects(version_id, update_data)
        await update_csv_file(version_id)
    finally:
        mission_score_collection = get_mission_score_collection()
        await mission_score_collection.update_many({
            'mission_id': version_id
        }, {
            '$set': {
                'task_updating': None,
            }
        })
        collection = get_mission_update_score_status()
        await collection.update_many({
            'version_id':  version_id,
            'user_id': user_id,
        },{
            '$set': {
                'update_status': 'SUCCESS'
            }
        })
        
    mission = await vdaService.get_mission_detail(version_id)
    mail_body = share_mission_html(f'Mission {mission.get("missionname")} Score Updated',
                                    f'The score for mission {mission.get("missionname")} has been updated and is ready to review. Please click on this <a href="{settings.fe_host}/data/{version_id}">link</a> to view the data.')

    subject = f'Mission {mission.get("missionname")} Score Updated'
    
    await mail_service.send_mail(user_email, email_template.EmailTemplate(mail_body), subject)
    return True

def share_mission_html(h, s):
    return f"""
        {header.Header(h)}
        {sub_header.SubHeader(s)}
    """

def get_celery_task_status(task_id: str) -> AsyncResult:
    return celery_app.AsyncResult(task_id)


def revoke_celery_task(task_id: str) -> None:
    celery_app.control.revoke(task_id, terminate=True, signal="SIGKILL")
