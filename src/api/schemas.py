# pylint: disable=too-few-public-methods

"""
Provides a bunch of Marshmallow Schemas to validate rainfall data processed through the API.
"""

from typing import Optional, Union

from flasgger import Schema, fields

from src.core.utils.enums.time_modes import TimeMode


class BaseSchema(Schema):
    """
    Base schema for depicting a value linked to rainfall data.
    It could be either float values or integer values (rainfall/years).
    Should be used as a parent class.
    """
    name: str = fields.Str()
    value: Union[float, int] = fields.Number()
    begin_year: int = fields.Int()
    end_year: Optional[int] = fields.Int(allow_none=True)
    time_mode: str = fields.Str(load_default=TimeMode.YEARLY.value)
    month: Optional[str] = fields.Str(allow_none=True)
    season: Optional[str] = fields.Str(allow_none=True)


class RainfallSchema(BaseSchema):
    """
    Schema for depicting a float value in mm (rainfall value).
    """
    value: float = fields.Float()


class RelativeDistanceToRainfallNormalSchema(RainfallSchema):
    """
    Schema for depicting a relative distance to rainfall normal for a yearly time mode.
    """
    normal_year: int = fields.Int()


class YearsAboveOrBelowNormalSchema(BaseSchema):
    """
    Schema for giving the number of years above or below rainfall normal for a yearly time mode.
    """
    normal_year: int = fields.Int()
    value: float = fields.Int()
