"""Category repository module"""
from typing import Optional, Dict, Union, List, Any
from mongoengine import QuerySet, DoesNotExist
from bson import ObjectId

from app.infra.database.models.user import User as UserModel
from app.infra.database.models.category import Category as CategoryModel
from app.infra.database.models.transaction import Transaction as TransactionModel
from app.domain.transaction.entity import TransactionInDB, TransactionInCreate, TransactionInUpdate
from app.domain.shared.enum import UserRole, Type
from app.shared.utils.general import date2datetime


class TransactionRepository:
    def __init__(self):
        pass

    def create(self, transaction: TransactionInCreate) -> TransactionInDB:
        """
        Create new transaction in db
        :param transaction:
        :return:
        """
        new_transaction = TransactionModel(**transaction.model_dump())
        # and save it to db
        new_transaction.save()

        return TransactionInDB.model_validate(new_transaction)

    def get_by_id(self, id: Union[str, ObjectId]) -> Optional[TransactionModel]:
        """
        Get category in db from id
        :param id:
        :return:
        """
        qs: QuerySet = TransactionModel.objects(id=id)
        # retrieve unique result
        # https://mongoengine-odm.readthedocs.io/guide/querying.html#retrieving-unique-results
        try:
            category: TransactionModel = qs.get()
            return category
        except DoesNotExist:
            return None

    def update(self, id: ObjectId, data: Union[TransactionInUpdate, Dict[str, Any]]) -> bool:
        try:
            data = data.model_dump(exclude_none=True) if isinstance(data, TransactionInUpdate) else data
            TransactionModel.objects(id=id).update_one(**data, upsert=False)
            return True
        except Exception:
            return False

    def count(self, conditions: Dict[str, Union[str, bool, ObjectId]] = {}) -> int:
        try:
            return TransactionModel._get_collection().count_documents(conditions)
        except Exception:
            return 0

    def find(self, conditions: Dict[str, Union[str, bool, ObjectId]]) -> List[Optional[TransactionModel]]:
        try:
            docs = TransactionModel._get_collection().find(conditions)
            return [TransactionModel.from_mongo(doc) for doc in docs] if docs else []
        except Exception:
            return []

    def list(
        self,
        type: Type,
        user: ObjectId,
        category: ObjectId,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        note: Optional[str] = None,
        sort: Optional[Dict[str, int]] = None,
    ) -> List[TransactionModel]:
        try:
            match_pipelines = {"type": type.value, "user": user}

            if category:
                match_pipelines = {
                    **match_pipelines,
                    "category": category
                }

            if note:
                note = note.lower()
                match_pipelines = {
                    **match_pipelines,
                    "note": {"$regex": ".*" + note + ".*"},
                }

            if date_from and date_to:
                match_pipelines = {
                    **match_pipelines,
                    "timestamp": {
                        "$gte": date2datetime(date_from),
                        "$lte": date2datetime(date_to, min_time=False),
                    },
                }

            pipeline = [
                {"$match": match_pipelines},
                sort if sort else {"$sort": {"_id": -1}},
            ]

            docs = TransactionModel.objects(user=user).aggregate(pipeline)
            data = [TransactionModel.from_mongo(doc) for doc in docs]
            res = []
            for d in data:
                if str(d['category']) in category:
                    res.append(d)
            return res
        except Exception:
            return []
