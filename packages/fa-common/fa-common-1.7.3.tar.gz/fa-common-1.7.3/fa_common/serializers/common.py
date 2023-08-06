from abc import ABC
from typing import Iterable, List, Optional, Tuple

from fa_common import CamelModel, DatabaseError
from fa_common.db import DocumentDBModel, WriteResult


class AbstractMeta(ABC):
    exclude: set = set()
    model: Optional[DocumentDBModel] = None
    write_only_fields: set = set()
    read_only_fields: set = set()


class Serializer(CamelModel):
    """
    Base Serializer class.
    Almost ALWAYS should be used in conjunction with
    `fa_common.core.serializers.openapi.patch` decorator to correctly handle
    inherited model fields and OpenAPI Schema generation with `response_model`.
    Responsible for sanitizing data & converting JSON to & from DocumentDBModel.
    Contains supplemental function, related to DocumentDBModel,
    mostly proxied to corresponding functions inside model (ex. save, update)
    Heavily uses `Meta` class for fine-tuning input & output. Main fields are:
        * exclude - set of fields that are excluded when serializing to dict
                    and sanitizing list of dicts
        * model - class of the DocumentDBModel to use, inherits fields from it
        * write_only_fields - set of fields that can be accepted in request,
                              but excluded when serializing to dict
        * read_only_fields - set of fields that cannot be accepted in request,
                              but included when serializing to dict
    Example usage:
    .. code-block:: python
        app = FastAPI()
        class SomeModel(DocumentDBModel):
            field1: str
        @openapi.patch
        class SomeSerializer(Serializer):
            read_only1: str = "const"
            write_only2: int
            not_visible: str = "42"
            class Meta:
                model = SomeModel
                exclude = {"not_visible"}
                write_only_fields = {"write_only2"}
                read_only_fields = {"read_only1"}
        @app.get("/", response_model=SomeSerializer.response_model)
        async def root(serializer: SomeSerializer):
            model_instance = await serializer.save()
            return model_instance.dict()
    POST-ing to this route following JSON:
    .. code-block:: json
        {"read_only1": "a", "write_only2": 123, "field1": "b"}
    Should return following response:
    .. code-block:: json
        {"id": 1, "field1": "b", "read_only1": "const"}
    """

    @classmethod
    def sanitize_list(cls, iterable: Iterable) -> List[dict]:
        """
        Sanitize list of rows that comes from DB to not include `exclude` set.
        :param iterable: sequence of dicts with model fields (from rows in DB)
        :return: list of cleaned, without `excluded`, dicts with model rows
        """

        def clean_d(d):
            if hasattr(cls.Meta, "exclude"):
                for e in cls.Meta.exclude:
                    d.pop(e, None)
                return d
            return d

        return list(map(lambda x: clean_d(x), iterable))

    async def save(
        self,
        include: set = None,
        exclude: set = None,
        rewrite_fields: dict = None,
    ) -> Optional[str]:
        """
        If we have `model` attribute in Meta, it populates model with data
        and saves it in DB, returning instance of model.
        :param rewrite_fields: dict of fields with values that override any
                other values for these fields right before inserting into DB.
                This is useful when you need to set some value explicitly
                based on request (e.g. user or token).
        :param include: fields to include from model in DB insert command
        :param exclude: fields to exclude from model in DB insert command
        :return: id (str) that was saved
        """
        if hasattr(self, "Meta") and getattr(self.Meta, "model", None) is not None:
            instance = self.Meta.model.__class__(**self.__values__)  # type: ignore
            ret = await instance.save(include=include, exclude=exclude, rewrite_fields=rewrite_fields)
            return ret
        return None

    async def update_one(self, _id: str, _data: dict, skip_defaults: bool = True) -> WriteResult:
        """
        If we have `model` attribute in Meta, it proxies filters & update data
        and after that returns actual result of update operation.
        :return: result of update operation
        """
        if hasattr(self, "Meta") and getattr(self.Meta, "model", None) is not None:
            fields = self.dict(skip_defaults=skip_defaults)
            if "exclude" in fields:
                for e in fields["exclude"]:
                    if e in _data:
                        del _data[e]

            return await self.Meta.model.update_one(_id, _data)  # type: ignore
        raise DatabaseError(f"No Meta.model is defined for {self.__class__}")

    async def update_many(self, data: List[Tuple[str, dict]], skip_defaults: bool = True) -> WriteResult:
        """
        If we have `model` attribute in Meta, it proxies filters & update data
        and after that returns actual result of update operation.
        :return: result of update many operation
        """
        if hasattr(self, "Meta") and getattr(self.Meta, "model", None) is not None:

            fields = self.dict(skip_defaults=skip_defaults)
            for k, v in data:
                if "exclude" in fields:
                    for e in fields["exclude"]:
                        if e in v:
                            del v[e]

            return await self.Meta.model.update_many(data=data)  # type: ignore
        raise DatabaseError(f"No Meta.model is defined for {self.__class__}")

    def dict(self, *args, **kwargs) -> dict:
        """
        Removes excluded fields based on `Meta` and `kwargs`
        :return: dict of serializer data fields
        """
        exclude = kwargs.get("exclude")
        if not exclude:
            exclude = set()

        if hasattr(self.Meta, "exclude") and self.Meta.exclude:
            exclude.update(self.Meta.exclude)

        if hasattr(self.Meta, "write_only_fields") and self.Meta.write_only_fields:
            exclude.update(self.Meta.write_only_fields)

        kwargs.update({"exclude": exclude})
        original = super().dict(*args, **kwargs)
        return original

    class Meta(AbstractMeta):
        ...


# class CamelSerializer(Serializer, CamelModel):
#     ...


class ModelSerializer(Serializer):
    """
    Left as a proxy for correct naming until we figure out how to inherit
    all the specific to model-handling methods and fields directly in here.
    """

    ...
