from src.utils.router import APIRouter
from src.resources.user.user_service import user_service
from fastapi_utils.tasks import repeat_every
import logging

router = APIRouter(
    prefix="/user_tasks",
    tags=["UserTasks"],
)

class UserTasksService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @router.on_event('startup')
    @repeat_every(seconds=60 * 5)
    async def sync_user_from_vda():
        await user_service.sync_user_from_vda()

    @router.on_event('startup')
    @repeat_every(seconds=60 * 7)
    async def sync_delete_user_with_vda():
        await user_service.sync_delete_user_with_vda()


user_taks_service = UserTasksService()