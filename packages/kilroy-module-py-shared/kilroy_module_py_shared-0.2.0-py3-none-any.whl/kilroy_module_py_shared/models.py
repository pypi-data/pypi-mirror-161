from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Annotated, Dict, List, Literal, Union
from uuid import UUID

from humps import camelize
from jsonschema.exceptions import SchemaError
from jsonschema.validators import Draft202012Validator
from pydantic import BaseModel, Field

from kilroy_module_py_shared.types import JSON


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


class BaseModuleModel(BaseModel, ABC):
    def json(self, *args, by_alias: bool = True, **kwargs) -> str:
        return super().json(*args, by_alias=by_alias, **kwargs)

    class Config:
        allow_population_by_field_name = True
        alias_generator = camelize


class PostSchema(BaseModuleModel):
    post_schema: JSONSchema


class StatusEnum(str, Enum):
    loading = "loading"
    ready = "ready"


class Status(BaseModuleModel):
    status: StatusEnum


class StatusNotification(BaseModuleModel):
    old: Status
    new: Status


class Config(BaseModuleModel):
    config: JSON


class ConfigSchema(BaseModuleModel):
    config_schema: JSONSchema


class ConfigNotification(BaseModuleModel):
    old: Config
    new: Config


class ConfigSetRequest(BaseModuleModel):
    set: Config


class ConfigSetReply(BaseModuleModel):
    old: Config
    new: Config


class GenerateRequest(BaseModuleModel):
    number_of_posts: int


class GenerateReply(BaseModuleModel):
    post_number: int
    post_id: UUID
    post: JSON


class FitPostsRequest(BaseModuleModel):
    post_number: int
    post: JSON


class FitPostsReply(BaseModuleModel):
    success: Literal[True]


class PostScore(BaseModuleModel):
    post_id: UUID
    score: float


class FitScoresRequest(BaseModuleModel):
    scores: List[PostScore]


class FitScoresReply(BaseModuleModel):
    success: Literal[True]


class StepRequest(BaseModuleModel):
    pass


class StepReply(BaseModuleModel):
    success: Literal[True]


class MetricTypeEnum(str, Enum):
    series = "series"
    timeseries = "timeseries"


class BaseMetricInfo(BaseModuleModel):
    label: str


class BaseSeriesMetricInfo(BaseMetricInfo):
    step_label: str
    value_label: str


class SeriesMetricInfo(BaseSeriesMetricInfo):
    type: Literal[MetricTypeEnum.series] = MetricTypeEnum.series
    step_type: Literal["int", "float"]
    value_type: Literal["int", "float"]


class TimeseriesMetricInfo(BaseSeriesMetricInfo):
    type: Literal[MetricTypeEnum.timeseries] = MetricTypeEnum.timeseries
    value_type: Literal["int", "float"]


MetricInfo = Annotated[
    Union[
        SeriesMetricInfo,
        TimeseriesMetricInfo,
    ],
    Field(discriminator="type"),
]


class MetricsInfo(BaseModuleModel):
    metrics: Dict[str, MetricInfo]


class SeriesMetricNotificationData(BaseModuleModel):
    type: Literal[MetricTypeEnum.series] = MetricTypeEnum.series
    step: float
    value: float


class TimeseriesMetricNotificationData(BaseModuleModel):
    type: Literal[MetricTypeEnum.timeseries] = MetricTypeEnum.timeseries
    step: datetime = Field(default_factory=datetime.utcnow)
    value: float


MetricNotificationData = Annotated[
    Union[
        SeriesMetricNotificationData,
        TimeseriesMetricNotificationData,
    ],
    Field(discriminator="type"),
]


class MetricsNotification(BaseModuleModel):
    name: str
    data: MetricNotificationData
