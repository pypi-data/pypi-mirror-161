"""
Time series data
"""

from typing import Union, Callable, List
from pandas import DataFrame, Series, merge

_CALCULATION_PRECISION = 12
_X_SUFFIX = '__x'
_Y_SUFFIX = '__y'
_VALUE = 'value'
_VALUE_X = _VALUE + _X_SUFFIX
_VALUE_Y = _VALUE + _Y_SUFFIX
_UNIT = 'unit'
_SYS_INVENTORY_ITEM_ID = 'sys_inventoryItemId'
_RESOLUTION_TIME_UNIT = 'resolution.timeUnit'
_RESOLUTION_FACTOR = 'resolution.factor'
_CORE_MERGE_FIELDS = ['timestamp', _RESOLUTION_TIME_UNIT, _RESOLUTION_FACTOR]
_MERGE_FIELDS = ['activity.code', 'pollutant.code', 'region.code', 'version.code']
_CALCULATE_RESULT_FIELDS = [_VALUE, _UNIT, _RESOLUTION_TIME_UNIT, _RESOLUTION_FACTOR] + _MERGE_FIELDS
_MERGE_FROM_RESULT_FIELDS = [_SYS_INVENTORY_ITEM_ID, _VALUE, _UNIT, _RESOLUTION_TIME_UNIT, _RESOLUTION_FACTOR] + _MERGE_FIELDS

CalcTypes = Union[int, float, 'TimeSeries']

def _get_fields_with_values(fields: List[str], data_frame: DataFrame) -> List[str]:
    return list(filter(lambda field: data_frame[field].notna().any(), fields))

def _calculate_with_data_frame(
    data_frame: DataFrame,
    other_data_frame: DataFrame,
    calculate: Callable[[Series, Series], Series],
    precision: int
    ) -> DataFrame:

    data_frame_fields = _get_fields_with_values(_MERGE_FIELDS, data_frame)
    other_data_frame_fields = _get_fields_with_values(_MERGE_FIELDS, other_data_frame)

    if len(data_frame_fields) >= len(other_data_frame_fields):
        merge_fields = _CORE_MERGE_FIELDS + other_data_frame_fields
        merge_validate = 'many_to_one'
        rename_fields = list(set(_MERGE_FIELDS) - set(other_data_frame_fields))
        rename_suffix = _X_SUFFIX
    else:
        merge_fields = _CORE_MERGE_FIELDS + data_frame_fields
        merge_validate = 'one_to_many'
        rename_fields = list(set(_MERGE_FIELDS) - set(data_frame_fields))
        rename_suffix = _Y_SUFFIX

    merged_data_frame = merge(
        data_frame,
        other_data_frame,
        on=merge_fields,
        how='inner',
        validate=merge_validate,
        suffixes=(_X_SUFFIX, _Y_SUFFIX))

    # NOTE: Calculations with respect to units and setting the right resulting unit is out of scope for the prototype and may be implemented later
    calculated_series = calculate(merged_data_frame[_VALUE_X], merged_data_frame[_VALUE_Y])
    merged_data_frame[_VALUE] = calculated_series.round(precision)

    rename_columns = {value + rename_suffix: value for value in [_UNIT] + rename_fields}
    merged_data_frame.rename(columns=rename_columns, inplace=True)

    return merged_data_frame[_CALCULATE_RESULT_FIELDS]

def _calculate_with_number(
    data_frame: DataFrame,
    number: Union[int, float],
    calculate: Callable[[Series, Union[int, float]], Series],
    precision: int
    ) -> DataFrame:
    # NOTE: Calculations with respect to units and setting the right resulting unit is out of scope for the prototype and may be implemented later
    calculated_series = calculate(data_frame[_VALUE], number)

    copied_data_frame = data_frame.copy(deep=True)
    copied_data_frame[_VALUE] = calculated_series.round(precision)
    return copied_data_frame[_CALCULATE_RESULT_FIELDS]

class TimeSeries:
    """
    Time series data
    """

    def __init__(self, data_frame: DataFrame) -> None:
        self._data_frame = data_frame

    def round(self, precision: int) -> 'TimeSeries':
        assert 0 <= precision <= 20
        copied_data_frame = self._data_frame.copy(deep=True)
        copied_data_frame[_VALUE] = copied_data_frame[_VALUE].round(precision)
        return TimeSeries(copied_data_frame)

    def set_value(self, value: Union[int, float]) -> None:
        rounded_value = round(value, _CALCULATION_PRECISION)
        self._data_frame.loc[:, _VALUE] = rounded_value

    def __add__(self, other: CalcTypes) -> 'TimeSeries':
        return self._calculate(lambda series, other_series: series + other_series, other)

    def __sub__(self, other: CalcTypes) -> 'TimeSeries':
        return self._calculate(lambda series, other_series: series - other_series, other)

    def __mul__(self, other: CalcTypes) -> 'TimeSeries':
        return self._calculate(lambda series, other_series: series * other_series, other)

    def __truediv__(self, other: CalcTypes) -> 'TimeSeries':
        return self._calculate(lambda series, other_series: series / other_series, other)

    def __iter__(self):
        return self._get_data_points().__iter__()

    def __getitem__(self, index: int):
        return self._get_data_points().__getitem__(index)

    def __len__(self):
        return self._get_data_points().__len__()

    def __str__(self) -> str:
        return self._data_frame.__str__()

    def __repr__(self) -> str:
        if hasattr(self, '_data_frame'):
            return self._data_frame.__repr__()
        return 'no data frame'

    def _repr_html_(self) -> Union[str, None]:
        if hasattr(self, '_data_frame'):
            # pylint: disable=protected-access
            return self._data_frame._repr_html_()
        return None

    def _get_data_points(self) -> Series:
        return self._data_frame[_VALUE]

    def _merge_values_from(self, other: 'TimeSeries') -> DataFrame:
        # pylint: disable=protected-access
        data_frame = self._data_frame
        other_data_frame = other._data_frame

        merged_data_frame = merge(
            data_frame,
            other_data_frame,
            on=_CORE_MERGE_FIELDS + _MERGE_FIELDS,
            how='inner',
            validate='one_to_one',
            suffixes=(_X_SUFFIX, _Y_SUFFIX))

        rename_columns = {value + _X_SUFFIX: value for value in [_SYS_INVENTORY_ITEM_ID] + list(_MERGE_FIELDS)}
        rename_columns[_VALUE + _Y_SUFFIX] = _VALUE
        # NOTE: Calculations with respect to units and setting the right resulting unit is out of scope for the prototype and may be implemented later
        rename_columns[_UNIT + _Y_SUFFIX] = _UNIT
        merged_data_frame.rename(columns=rename_columns, inplace=True)

        result_data_frame = merged_data_frame[_MERGE_FROM_RESULT_FIELDS]
        return result_data_frame

    def _calculate(self, calculate: Callable[[Series, Union[Series, int, float]], Series], other: CalcTypes) -> 'TimeSeries':
        if isinstance(other, TimeSeries):
            # pylint: disable=protected-access
            calculated_data_frame = _calculate_with_data_frame(self._data_frame, other._data_frame, calculate, _CALCULATION_PRECISION)
        elif isinstance(other, (int, float)):
            calculated_data_frame = _calculate_with_number(self._data_frame, other, calculate, _CALCULATION_PRECISION)
        else:
            raise ValueError(f'Unsupported type {type(other)}.')
        return TimeSeries(calculated_data_frame)
