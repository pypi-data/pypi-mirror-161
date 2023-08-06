from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from humps import camelize
from jsonschema.exceptions import SchemaError
from jsonschema.validators import Draft202012Validator
from pydantic import BaseModel

from kilroy_face_py_shared.types import JSON


class JSONSchema(dict):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, schema: JSON) -> JSON:
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as e:
            raise ValueError(
                "Schema is not a valid JSON Schema 2020-12."
            ) from e
        if "type" not in schema:
            raise ValueError("Schema should have a type field.")
        elif schema["type"] != "object":
            raise ValueError("Only object types are allowed.")
        return schema


class BaseFaceModel(BaseModel, ABC):
    def json(self, *args, by_alias: bool = True, **kwargs) -> str:
        return super().json(*args, by_alias=by_alias, **kwargs)

    class Config:
        allow_population_by_field_name = True
        alias_generator = camelize


class PostSchema(BaseFaceModel):
    post_schema: JSONSchema


class StatusEnum(str, Enum):
    loading = "loading"
    ready = "ready"


class Status(BaseFaceModel):
    status: StatusEnum


class StatusNotification(BaseFaceModel):
    old: Status
    new: Status


class Config(BaseFaceModel):
    config: JSON


class ConfigSchema(BaseFaceModel):
    config_schema: JSONSchema


class ConfigNotification(BaseFaceModel):
    old: Config
    new: Config


class ConfigSetRequest(BaseFaceModel):
    set: Config


class ConfigSetReply(BaseFaceModel):
    old: Config
    new: Config


class PostRequest(BaseFaceModel):
    post: JSON


class PostReply(BaseFaceModel):
    post_id: UUID


class ScoreRequest(BaseFaceModel):
    post_id: UUID


class ScoreReply(BaseFaceModel):
    score: float


class ScrapRequest(BaseFaceModel):
    limit: Optional[int] = None
    before: Optional[datetime] = None
    after: Optional[datetime] = None


class ScrapReply(BaseFaceModel):
    post_number: int
    post_id: UUID
    post: JSON
