from datetime import datetime
from optparse import Option
from typing import Any, List, Optional, Dict

from pydantic import Field
from pydantic_yaml import YamlModel, YamlStrEnum


class DatasetSourceType(YamlStrEnum):
    CSV = 'CSV'
    RASGO = 'RASGO'
    TABLE = 'TABLE'
    DATAFRAME = 'DATAFRAME'


class RasgoVersion(YamlStrEnum):
    V20 = '2.0'


class BaseV2(YamlModel):
    schema_version: RasgoVersion = RasgoVersion.V20

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class OfflineOperation(BaseV2):
    resource_key: Optional[str]
    operation_name: str
    operation_args: Optional[Dict[str, Any]]
    transform_name: Optional[str]
    dependencies: Optional[List[str]]
    fqtn: str


class OfflineOperationSet(BaseV2):
    resource_key: Optional[str]
    operations: Optional[List[OfflineOperation]]
    dependencies: Optional[List[str]]
    sql: Optional[str]


class OfflineInsight(BaseV2):
    name: Optional[str]
    transform_name: str
    transform_arguments: Optional[Dict[str, Any]]


class OfflineFilter(BaseV2):
    column_name: str
    operator: str
    comparison_value: str


class OfflineMetric(BaseV2):
    name: str
    aggregation_type: str
    target_expression: str
    time_grains: List[str]
    time_dimension: str
    dimensions: List[str]

    filters: Optional[List[OfflineFilter]]
    meta: Optional[Dict[str, str]]
    label: Optional[str]
    description: Optional[str]

    recent_values: Optional[List]
    recent_time_grain: Optional[str]
    recent_period_start: Optional[datetime]
    recent_period_end: Optional[datetime]


class OfflineColumn(BaseV2):
    name: str
    data_type: str


class OfflineDataset(BaseV2):
    name: str
    resource_key: str
    description: Optional[str]
    status: Optional[str]
    source_type: Optional[DatasetSourceType] = DatasetSourceType.RASGO
    organization_id: int

    attributes: Optional[Dict[str, str]]
    tags: Optional[List[str]]

    dw_operation_set: Optional[OfflineOperationSet]
    columns: Optional[List[OfflineColumn]]
    metrics: Optional[List[OfflineMetric]]
    insights: Optional[List[OfflineInsight]]

    fqtn: Optional[str]
