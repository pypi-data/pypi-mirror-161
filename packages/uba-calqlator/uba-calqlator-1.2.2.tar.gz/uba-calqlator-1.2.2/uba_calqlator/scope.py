"""
A scope for time series data with a time range and an inventory name.
"""

import math
import re
from pandas import DataFrame, Series
from typing import List, Union
from seven2one import TechStack
from .utils import _parse_timepoint
from .timeseries import TimeSeries

_FIELDS = ['sys_inventoryItemId', 'unit', 'resolution.timeUnit', 'resolution.factor', 'activity.code',
    'pollutant.code', 'region.code', 'version.code', 'value_type.code']
_INCLUDE_MISSING = True
_DISPLAY_MODE = 'rows'
_TIMEPOINT_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
_FLAG_VALID = 'VALID'
_FLAG_MISSING = 'MISSING'

def _get_time_series_data(inventory_id: str, data_frame: DataFrame) -> dict:

    def _is_missing(value) -> bool:
        return ((value is None) or
            ((isinstance(value, float) or isinstance(value, int)) and math.isnan(value)))

    def _get_data_point(item):
        timestamp = item[0].strftime(_TIMESTAMP_FORMAT)
        value = item[1]
        flag = _FLAG_VALID

        if _is_missing(value):
            value = 0
            flag = _FLAG_MISSING

        return {
            'timestamp': timestamp,
            'value': value,
            'flag': flag
        }

    def _get_data_points(data_frame: DataFrame) -> dict:
        unit = data_frame.name[0]
        resolution_time_unit = data_frame.name[1]
        resolution_factor = data_frame.name[2]
        data_points = [_get_data_point(item) for item in zip(data_frame.index, data_frame.value)]
        return {
            'resolution': { 'timeUnit': resolution_time_unit, 'factor': resolution_factor },
            'unit': unit,
            'dataPoints': data_points
        }

    def _get_data(data_frame: DataFrame) -> Series:
        data = (data_frame
            .groupby(['unit', 'resolution.timeUnit', 'resolution.factor'])
            .apply(_get_data_points)
            .reset_index()
            .rename(columns={0: 'data'}))
        return data['data']

    data_frame['sys_inventoryId'] = inventory_id
    time_series_data = (data_frame
        .groupby(['sys_inventoryId', 'sys_inventoryItemId'])
        .apply(_get_data)
        .reset_index()
        .rename(columns={0: 'data'})
        .to_dict(orient='records'))
    return time_series_data

def _is_inventory_item_id(value) -> bool:
    return (isinstance(value, str) and
        re.match('^[a-zA-Z0-9]{8,12}$', value) is not None)

class Scope:
    """
    A scope for time series data with a time range and an inventory name.
    """

    def __init__(self, client: TechStack, inventory_name: str, from_timepoint: str, to_timepoint: str):
        self._client = client
        self._inventory_name = inventory_name
        self._inventory_id = client.structure[inventory_name]['inventoryId']
        self._from_timepoint = _parse_timepoint(from_timepoint, is_begin=True)
        self._to_timepoint = _parse_timepoint(to_timepoint, is_begin=False)

    def time_series(self, where: Union[List[str], str]) -> TimeSeries:
        if _is_inventory_item_id(where):
            where = f'sys_inventoryItemId eq "{where}"'

        data_frame = self._client.TimeSeries.timeSeriesData(
            self._inventory_name,
            self._from_timepoint.strftime(_TIMEPOINT_FORMAT),
            self._to_timepoint.strftime(_TIMEPOINT_FORMAT),
            fields=_FIELDS,
            where=where,
            displayMode=_DISPLAY_MODE,
            includeMissing=_INCLUDE_MISSING)
        return TimeSeries(data_frame)

    def write(self, where: Union[List[str], str], time_series: TimeSeries) -> None:

        target_time_series = self.time_series(where)

        # pylint: disable=protected-access
        data_frame = target_time_series._merge_values_from(time_series)
        time_series_data = _get_time_series_data(self._inventory_id, data_frame)
        self._client.TimeSeries.setTimeSeriesDataCollection(time_series_data)
