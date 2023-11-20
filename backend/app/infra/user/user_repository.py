"""User repository module"""
from typing import Optional, Dict, Union, List, Any
from mongoengine import QuerySet, DoesNotExist
from bson import ObjectId

from app.infra.database.models.user import User as UserModel
from app.domain.user.entity import UserInDB, UserInCreate, UserInUpdate
from app.domain.shared.enum import UserRole


class UserRepository:
    def __init__(self):
        pass

    def create(self, user: UserInCreate) -> UserInDB:
        """
        Create new user in db
        :param user:
        :return:
        """
        # create user document instance
        new_user = UserModel(**user.model_dump())
        # and save it to db
        new_user.save()

        return UserInDB.model_validate(new_user)

    def get_by_id(self, user_id: Union[str, ObjectId]) -> Optional[UserModel]:
        """
        Get user in db from id
        :param user_id:
        :return:
        """
        qs: QuerySet = UserModel.objects(id=user_id)
        # retrieve unique result
        # https://mongoengine-odm.readthedocs.io/guide/querying.html#retrieving-unique-results
        try:
            user: UserModel = qs.get()
            return user
        except DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[UserModel]:
        """
        Get user in db from email
        :param user_id:
        :return:
        """
        qs: QuerySet = UserModel.objects(email=email)
        # retrieve unique result
        # https://mongoengine-odm.readthedocs.io/guide/querying.html#retrieving-unique-results
        try:
            user = qs.get()
        except DoesNotExist:
            return None
        return user

    def update(self, id: ObjectId, data: Union[UserInUpdate, Dict[str, Any]]) -> bool:
        try:
            data = data.model_dump(exclude_none=True) if isinstance(data, UserInUpdate) else data
            UserModel.objects(id=id).update_one(**data, upsert=False)
            return True
        except Exception:
            return False

    def count(self, conditions: Dict[str, Union[str, bool, ObjectId]] = {}) -> int:
        try:
            return UserModel._get_collection().count_documents(conditions)
        except Exception:
            return 0

    def list(
        self,
        role: UserRole,
        email: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 100,
        sort: Optional[Dict[str, int]] = None,
    ) -> List[UserModel]:
        try:
            match_pipelines = {"role": role.value}
            if email:
                email = email.lower()
                match_pipelines = {
                    **match_pipelines,
                    "email": {"$regex": ".*" + email + ".*"},
                }
            pipeline = [
                {"$match": match_pipelines},
                sort if sort else {"$sort": {"_id": -1}},
                {"$skip": page_size * (page_index - 1)},
                {"$limit": page_size},
            ]
            docs = UserModel.objects().aggregate(pipeline)
            return [UserModel.from_mongo(doc) for doc in docs]
        except Exception:
            return []
