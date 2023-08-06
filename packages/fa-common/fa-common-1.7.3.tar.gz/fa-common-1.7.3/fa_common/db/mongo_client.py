from typing import Any, List, Optional, Tuple, Type

# from pymongo.cursor import Cursor
# from pymongo.results import InsertOneResult, UpdateResult
import pymongo
from bson import CodecOptions
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

# from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from fa_common import get_current_app, get_timezone
from fa_common import logger as LOG

from .base_client import BaseClient
from .models import (
    DBIndex,
    DeleteResult,
    DocumentDBModel,
    FireOffset,
    Operator,
    SortOrder,
    WhereCondition,
    WriteResult,
)


class MongoDBClient(BaseClient):
    """
    Singleton client for interacting with MongoDB.
    Operates mostly using models, specified when making DB queries.

    Implements only part of internal `motor` methods, but can be populated more.

    Please don't use it directly, use `scidra.core.db.utils.get_db_client`.
    """

    __instance = None
    mongodb: AsyncIOMotorClient = None
    codec_options: CodecOptions = None

    def __new__(cls) -> "MongoDBClient":
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            tzinfo = get_timezone()
            cls.__instance.codec_options = CodecOptions(tz_aware=True, tzinfo=tzinfo)
            cls.__instance.mongodb = app.mongodb  # type: ignore
        return cls.__instance

    def get_collection(self, collection_name: str) -> Collection:
        return self.mongodb.get_collection(collection_name, codec_options=self.codec_options)

    async def delete_collection(self, collection_name: str):
        await self.mongodb.drop_collection(collection_name)

    async def insert(
        self,
        model: DocumentDBModel,
        include=None,
        exclude=None,
        session: Any = None,
    ) -> WriteResult:
        data = model.dict(include=include, exclude=exclude)
        _id = data.pop("id", None)
        if _id is not None:
            data["_id"]
        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        result = await collection.insert_one(data, session=session)

        LOG.info("Insert Result: {}", result)
        return WriteResult(new_id=str(result.inserted_id), transform_results=[result])

    async def count(self, model: Type[DocumentDBModel], session: Any = None) -> int:

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        res = await collection.count_documents(session=session)
        return res

    async def delete(self, model: Type[DocumentDBModel], _id: str, session: Any = None) -> DeleteResult:

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        await collection.delete_one(filter={"_id": ObjectId(_id)}, session=session)
        return DeleteResult()

    async def update_one(
        self, model: Type[DocumentDBModel], _id: str, data: dict, session: Any = None
    ) -> WriteResult:
        data.pop("id", None)

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        await collection.update_one(filter={"_id": ObjectId(_id)}, update={"$set": data}, session=session)
        return WriteResult()

    # FIXME: Add this back once the firstore version has been fixed and added
    # async def update_many(
    #     self, model: Type[DocumentDBModel], data: List[Tuple[str, dict]]
    # ) -> WriteResult:
    #     _id = filter_kwargs.pop("id", None)
    #     if _id is not None:
    #         filter_kwargs["_id"] = _id

    #     collection_name = model.get_db_collection()
    #     collection = self.get_collection(collection_name)users
    #     res = await collection.update_many(filter_kwargs, kwargs, session=session)
    #     return res

    async def get(
        self, model: Type[DocumentDBModel], _id: str, session: Any = None
    ) -> Optional[DocumentDBModel]:

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        res = await collection.find_one(filter={"_id": ObjectId(_id)}, session=session)
        if res is None:
            return None

        return model(**res)

    async def list(
        self,
        model: Type[DocumentDBModel],
        where: List[WhereCondition] = [],
        _limit: int = 0,
        _sort: List[Tuple[str, SortOrder]] = None,
        mongo_offset: int = 0,
        fire_offset: FireOffset = None,
    ) -> List[DocumentDBModel]:

        collection_name = model.get_db_collection()
        results = await self.list_dict(collection_name, where, _limit, _sort, mongo_offset, fire_offset)

        return [model(**res) for res in results]

    def generate_id(self, collection_name: str) -> str:
        """
        Generator of IDs for newly created MongoDB rows.
        :return: `bit_size` long int
        """
        return ""

    async def find_one(
        self,
        model: Type[DocumentDBModel],
        where: List[WhereCondition] = [],
        session: Any = None,
    ) -> Optional[DocumentDBModel]:
        results = await self.list(model, where, 1)
        if len(results) > 0:
            return results[0]
        else:
            return None

    async def find_one_dict(
        self,
        collection_name: str,
        where: List[WhereCondition] = [],
        session: Any = None,
    ) -> Optional[dict]:
        results = await self.list_dict(collection_name, where, 1)
        if len(results) > 0:
            return results[0]
        else:
            return None

    async def get_dict(
        self,
        collection_name: str,
        _id: str,
        session: Any = None,
    ) -> Optional[dict]:
        collection = self.get_collection(collection_name)
        res = await collection.find_one(filter={"_id": ObjectId(_id)}, session=session)
        if res is None:
            return None

        return res

    async def list_dict(
        self,
        collection_name: str,
        where: List[WhereCondition] = [],
        _limit: int = 0,
        _sort: List[Tuple[str, SortOrder]] = None,
        mongo_offset: int = 0,
        fire_offset: FireOffset = None,
    ) -> List[dict]:
        collection = self.get_collection(collection_name)

        filter_dict = {}
        for wc in where:
            if wc.operator is Operator.EQUALS:
                filter_dict[wc.field] = wc.value
            elif wc.operator is Operator.LT:
                filter_dict[wc.field] = {"$lt": wc.value}
            elif wc.operator is Operator.GT:
                filter_dict[wc.field] = {"$gt": wc.value}
            # TODO: Other array filters

        finder = collection.find(filter_dict, skip=mongo_offset, limit=_limit)
        if _sort is not None:
            for sort in _sort:
                finder.sort(sort[0], sort[1])
        docs = await finder.to_list(None)
        return docs

    async def create_indexes(self, index: List[DBIndex], collection: str) -> Optional[List[str]]:
        c = self.get_collection(collection)
        mongo_indexes = []
        for ind in index:
            fields = [
                (i[0], pymongo.ASCENDING if i[0] == SortOrder.ASCENDING else pymongo.DESCENDING)
                for i in ind.index_fields
            ]
            mongo_indexes.append(pymongo.IndexModel(fields, unique=ind.unique))
        return await c.create_indexes(mongo_indexes)
