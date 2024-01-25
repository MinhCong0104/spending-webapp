"""Category repository module"""
from typing import Optional, Dict, Union, List, Any
from mongoengine import QuerySet, DoesNotExist
from bson import ObjectId

from app.domain.user.entity import User
from app.infra.database.models.category import Category as CategoryModel
from app.domain.category.entity import CategoryInDB, CategoryInCreate, CategoryInUpdate
from app.domain.shared.enum import UserRole, Type


class CategoryRepository:
    def __init__(self):
        pass

    def create(self, category: CategoryInCreate) -> CategoryInDB:
        """
        Create new category in db
        :param category:
        :return:
        """
        new_category = CategoryModel(**category.model_dump())
        # and save it to db
        new_category.save()

        return CategoryInDB.model_validate(new_category)

    def get_by_id(self, id: Union[str, ObjectId]) -> Optional[CategoryModel]:
        """
        Get category in db from id
        :param id:
        :return:
        """
        qs: QuerySet = CategoryModel.objects(id=id)
        # retrieve unique result
        # https://mongoengine-odm.readthedocs.io/guide/querying.html#retrieving-unique-results
        try:
            category: CategoryModel = qs.get()
            return category
        except DoesNotExist:
            return None

    def get_by_name(self, name: str) -> Optional[CategoryModel]:
        qs: QuerySet = CategoryModel.objects(name=name)
        # retrieve unique result
        # https://mongoengine-odm.readthedocs.io/guide/querying.html#retrieving-unique-results
        try:
            category: CategoryModel = qs.get()
            return category
        except DoesNotExist:
            return None

    def update(self, id: ObjectId, data: Union[CategoryInUpdate, Dict[str, Any]]) -> bool:
        try:
            data = data.model_dump(exclude_none=True) if isinstance(data, CategoryInUpdate) else data
            CategoryModel.objects(id=id).update_one(**data, upsert=False)
            return True
        except Exception:
            return False

    def delete(self, id: ObjectId) -> bool:
        try:
            CategoryModel.objects(id=id).delete()
            return True
        except Exception:
            return False

    def count(self, conditions: Dict[str, Union[str, bool, ObjectId]] = {}) -> int:
        try:
            return CategoryModel._get_collection().count_documents(conditions)
        except Exception:
            return 0

    def list(
        self,
        user: ObjectId,
        type: Optional[Type] = None,
        name: Optional[str] = None,
        note: Optional[str] = None,
        sort: Optional[Dict[str, int]] = None,
    ) -> List[CategoryModel]:
        try:
            match_pipelines = {"user": user}

            if type:
                match_pipelines = {
                    **match_pipelines,
                    "type": type.value,
                }

            if note:
                note = note.lower()
                match_pipelines = {
                    **match_pipelines,
                    "note": {"$regex": ".*" + note + ".*"},
                }

            if name:
                name = name.lower()
                match_pipelines = {
                    **match_pipelines,
                    "name": {"$regex": ".*" + name + ".*"},
                }

            pipeline = [
                {"$match": match_pipelines},
                sort if sort else {"$sort": {"_id": -1}},
            ]
            docs = CategoryModel.objects().aggregate(pipeline)
            return [CategoryModel.from_mongo(doc) for doc in docs]
        except Exception:
            return []
