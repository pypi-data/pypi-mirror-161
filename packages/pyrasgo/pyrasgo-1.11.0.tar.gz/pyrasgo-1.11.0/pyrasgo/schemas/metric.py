from datetime import datetime, timedelta
from enum import Enum
from functools import total_ordering
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class Filter(BaseModel):
    column_name: str = Field(alias='columnName')
    operator: str
    comparison_value: str = Field(alias='comparisonValue')

    class Config:
        allow_population_by_field_name = True


@total_ordering
class TimeGrain(str, Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    QUARTER = "QUARTER"
    YEAR = "YEAR"

    def timedelta(self):
        if self.value == "HOUR":
            return timedelta(hours=1)
        if self.value == "DAY":
            return timedelta(days=1)
        if self.value == "WEEK":
            return timedelta(weeks=1)
        if self.value == "MONTH":
            return timedelta(days=30)
        if self.value == "QUARTER":
            return timedelta(days=91)
        if self.value == "YEAR":
            return timedelta(days=365)

    def __lt__(self, other):
        order = (TimeGrain.HOUR, TimeGrain.DAY, TimeGrain.WEEK, TimeGrain.MONTH, TimeGrain.QUARTER, TimeGrain.YEAR)
        if self.__class__ == other.__class__:
            return order.index(self) < order.index(other)
        raise NotImplemented

    def __gt__(self, other):
        order = (TimeGrain.HOUR, TimeGrain.DAY, TimeGrain.WEEK, TimeGrain.MONTH, TimeGrain.QUARTER, TimeGrain.YEAR)
        if self.__class__ == other.__class__:
            return order.index(self) > order.index(other)
        raise NotImplemented


class Metric(BaseModel):
    id: int
    name: str
    ds_dataset_id: int = Field(alias='datasetId')
    aggregation_type: str = Field(alias='aggregationType')
    target_expression: str = Field(alias='targetExpression')
    time_grains: List[str] = Field(alias='timeGrains')
    time_dimension: str = Field(alias='timeDimension')
    dimensions: List[str]

    filters: Optional[List[Filter]]
    meta: Optional[Dict[str, str]]
    label: Optional[str]
    description: Optional[str]

    recent_values: Optional[List] = Field(alias='recentValues')
    recent_time_grain: Optional[str] = Field(alias='recentTimeGrain')
    recent_period_start: Optional[datetime] = Field(alias='recentPeriodStart')
    recent_period_end: Optional[datetime] = Field(alias='recentPeriodEnd')

    class Config:
        allow_population_by_field_name = True


class MetricCreate(BaseModel):
    name: str
    ds_dataset_id: int = Field(alias='datasetId')
    aggregation_type: str = Field(alias='aggregationType')
    target_expression: str = Field(alias='targetExpression')
    time_grains: List[TimeGrain] = Field(alias='timeGrains')
    time_dimension: str = Field(alias='timeDimension')
    dimensions: List[str]

    filters: Optional[List[Filter]]
    meta: Optional[Dict[str, str]]
    label: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class MetricUpdate(BaseModel):
    id: int
    name: Optional[str]
    ds_dataset_id: Optional[int] = Field(alias='datasetId')
    aggregation_type: Optional[str] = Field(alias='aggregationType')
    target_expression: Optional[str] = Field(alias='targetExpression')
    time_grains: Optional[List[TimeGrain]] = Field(alias='timeGrains')
    time_dimension: Optional[str] = Field(alias='timeDimension')
    dimensions: Optional[List[str]]

    filters: Optional[List[Filter]]
    meta: Optional[Dict[str, str]]
    label: Optional[str]
    description: Optional[str]

    class Config:
        allow_population_by_field_name = True
