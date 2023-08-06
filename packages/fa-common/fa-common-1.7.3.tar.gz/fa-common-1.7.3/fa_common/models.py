from datetime import date, datetime, time, timezone

from bson import ObjectId
from humps.camel import case
from pydantic import BaseModel
from pydantic.datetime_parse import parse_datetime

from .utils import get_timezone


def to_camel(string):
    return case(string)


class utc_datetime(datetime):
    @classmethod
    def __get_validators__(cls):
        yield parse_datetime  # default pydantic behavior
        yield cls.ensure_tzinfo

    @classmethod
    def ensure_tzinfo(cls, v):
        # if TZ isn't provided, we assume UTC, but you can do w/e you need
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        # else we convert to utc
        return v.astimezone(timezone.utc)

    @staticmethod
    def to_str(dt: datetime) -> str:
        return dt.isoformat()  # replace with w/e format you want


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.replace(microsecond=0, tzinfo=get_timezone()).isoformat(),
            date: lambda date: date.isoformat(),
            time: lambda time: time.replace(microsecond=0, tzinfo=get_timezone()).isoformat(),
            ObjectId: lambda v: str(v),
        }
        # Needed for the _id to be included when serialised; can't work out how to rename it `id`
        fields = {"id": "_id"}


class FileDownloadRef(CamelModel):
    name: str
    url: str
    extension: str
    size: int
