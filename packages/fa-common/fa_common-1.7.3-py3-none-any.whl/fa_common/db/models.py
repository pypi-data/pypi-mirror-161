import abc
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Tuple

from pydantic import Field, root_validator, validator

from fa_common import CamelModel, get_now
from fa_common import logger as LOG

from .utils import get_db_client

# from pymongo.results import UpdateResult, DeleteResult


class SortOrder(str, Enum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class DBIndex(CamelModel):
    index_fields: List[Tuple[str, SortOrder]]
    unique: bool


class FireOffset(CamelModel):
    # Start at or Start After
    start_at: bool = False
    start_id: Optional[str] = None
    start_fields: Optional[dict] = None

    @root_validator
    def check_passwords_match(cls, values):
        pw1, pw2 = values.get("start_id"), values.get("start_field")
        if pw1 is None and pw2 is None:
            raise ValueError("Either start_id or start_fields needs a value")
        return values


class Operator(str, Enum):
    EQUALS = "=="
    LT = "<"
    GT = ">"
    IN = "in"
    ARRAY_CONTAINS = "array_contains"
    ARRAY_CONTAINS_ANY = "array_contains_any"


class WhereCondition(CamelModel):
    field: str
    operator: Operator = Operator.EQUALS
    value: Any


class WriteResult(CamelModel):
    success: bool = True
    new_id: Optional[str] = None
    transform_results: Optional[List[Any]]


class DeleteResult(CamelModel):
    success: bool = True
    delete_time: Optional[datetime]


class DocumentDBModel(CamelModel, abc.ABC):
    """
    Base Model to use for any information saving in MongoDB.
    Provides `id` field as a base, populated by id-generator.
    Use it as follows:

    .. code-block:: python

        class MyModel(DocumentDBModel):
            additional_field1: str
            optional_field2: int = 42

            class Meta:
                collection = "mymodel_collection"

        mymodel = MyModel(additional_field1="value")
        mymodel.save()
        assert mymodel.additional_field1 == "value"
        assert mymodel.optional_field2 == 42
        assert isinstance(mymodel.id, int)
    """

    id: Optional[str] = Field(None, alias="_id")

    @validator("id", pre=True)
    def split_str(cls, v):
        if v is None or isinstance(v, str):
            return v
        return str(v)

    def set_id(self) -> Optional[str]:
        """
        If id is supplied (ex. from DB) then use it, otherwise generate new.
        """
        if not self.id:
            db = get_db_client()
            self.id = db.generate_id(self.get_db_collection())

        return self.id

    @classmethod
    @abc.abstractmethod
    def get_db_collection(cls) -> str:
        pass

    @classmethod
    async def get(cls, _id: str) -> Optional["DocumentDBModel"]:
        db = get_db_client()
        result = await db.get(cls, _id)
        return result

    @classmethod
    async def find_one(cls, where: List[WhereCondition]) -> Optional["DocumentDBModel"]:
        db = get_db_client()
        result = await db.find_one(cls, where)
        return result

    @classmethod
    async def delete(cls, _id: str) -> DeleteResult:
        db = get_db_client()
        result = await db.delete(cls, _id)
        return result

    @classmethod
    async def count(cls) -> int:
        db = get_db_client()
        result = await db.count(cls)
        return result

    @classmethod
    async def list(
        cls,
        where: List[WhereCondition] = [],
        _limit: int = 0,
        _sort: List[Tuple[str, SortOrder]] = None,
        mongo_offset: int = 0,
        fire_offset: FireOffset = None,
    ) -> List["DocumentDBModel"]:
        db = get_db_client()
        return await db.list(
            cls,
            where,
            _limit=_limit,
            _sort=_sort,
            mongo_offset=mongo_offset,
            fire_offset=fire_offset,
        )

    async def save(
        self,
        include: set = None,
        exclude: set = None,
        rewrite_fields: dict = None,
    ) -> Optional[str]:
        db = get_db_client()
        # _id = self.set_id()

        if not rewrite_fields:
            rewrite_fields = {}

        for field, value in rewrite_fields.items():
            setattr(self, field, value)

        insert_result = await db.insert(self, include=include, exclude=exclude)
        LOG.debug(insert_result.transform_results)
        if not self.id:
            self.id = insert_result.new_id

        return self.id

    @classmethod
    async def update_one(cls, _id: str, data: dict) -> WriteResult:
        db = get_db_client()
        result = await db.update_one(cls, _id, data)
        return result

    @classmethod
    async def update_many(cls, data: List[Tuple[str, dict]]) -> WriteResult:
        db = get_db_client()
        result = await db.update_many(cls, data)
        return result

    @classmethod
    async def create_indexes(cls) -> Optional[List[str]]:
        if hasattr(cls, "Meta") and hasattr(cls.Meta, "indexes"):  # type:ignore
            db = get_db_client()
            return await db.create_indexes(cls, cls.Meta.indexes, cls.Meta.collection)  # type:ignore
        return None

    class Config:
        anystr_strip_whitespace = True


class DocumentDBTimeStampedModel(DocumentDBModel):
    """
    TimeStampedModel to use when you need to have `created` field,
    populated at your model creation time.

    Use it as follows:

    .. code-block:: python

        class MyTimeStampedModel(MongoDBTimeStampedModel):

            class Meta:
                collection = "timestamped_collection"


        mymodel = MyTimeStampedModel()
        mymodel.save()

        assert isinstance(mymodel.id, int)
        assert isinstance(mymodel.created, datetime)
    """

    created: Optional[datetime] = None

    @validator("created", pre=True, always=True)
    def set_created_now(cls, v: datetime) -> datetime:
        """
        If created is supplied (ex. from DB) -> use it, otherwise generate new.
        """
        if v:
            return v
        now = get_now()
        return now.replace(microsecond=0)
