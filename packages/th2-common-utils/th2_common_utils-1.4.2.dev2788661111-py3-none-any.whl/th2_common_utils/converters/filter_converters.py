#   Copyright 2022-2022 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from enum import Enum
from functools import singledispatch
from typing import Any, Dict, List, Optional, Union

from google.protobuf.duration_pb2 import Duration
from th2_grpc_common.common_pb2 import ListValueFilter, MessageFilter, MetadataFilter, NullValue, \
    RootComparisonSettings, RootMessageFilter, SimpleList, ValueFilter


class ProtobufDefaults(Enum):
    BOOL = False
    INT = 0


class FilterField(str, Enum):
    OPERATION = 'operation'
    KEY = 'key'
    VALUE = 'value'


MetadataDict = Dict[str, Any]


def dict_to_root_message_filter(message_type: str = '',
                                message_filter: Optional[Union[MetadataDict, MessageFilter]] = None,
                                metadata_filter: Optional[Union[MetadataDict, MetadataFilter]] = None,
                                ignore_fields: Optional[List[str]] = None,
                                check_repeating_group_order: bool = False,
                                time_precision: Optional[Duration] = None,
                                decimal_precision: str = '') -> RootMessageFilter:
    """Converts a dict to RootMessageFilter.

    Args:
        message_type: Message type.
        message_filter: Message filter as a dict or MessageFilter class instance.
        metadata_filter: Metadata filter as a dict or MetadataFilter class instance.
        ignore_fields: Fields to ignore (is used when creating filter's comparison settings).
        check_repeating_group_order: Whether check repeating group order or not (is used when creating filter's
            comparison settings).
        time_precision: Time precision (is used when creating filter's comparison settings).
        decimal_precision: Decimal Precision (is used when creating filter's comparison settings).

    Returns:
        RootMessageFilter class instance.

    Raises:
        TypeError: Occurs when MessageFilter or MetadataFilter as dicts contain a field of the unsupported type.
    """

    if message_filter is None:
        message_filter = MessageFilter()
    elif isinstance(message_filter, Dict):
        message_filter = dict_to_message_filter(message_filter)

    if metadata_filter is None:
        metadata_filter = MetadataFilter()
    elif isinstance(metadata_filter, Dict):
        metadata_filter = dict_to_metadata_filter(metadata_filter)

    return RootMessageFilter(messageType=message_type,
                             message_filter=message_filter,
                             metadata_filter=metadata_filter,
                             comparison_settings=RootComparisonSettings(
                                 ignore_fields=ignore_fields,
                                 check_repeating_group_order=check_repeating_group_order,
                                 time_precision=time_precision,
                                 decimal_precision=decimal_precision))


# =========================
# MessageFilter
# =========================

def dict_to_message_filter(dict_obj: Dict[str, Any]) -> MessageFilter:
    return MessageFilter(fields={
        filter_name: _create_value_filter(filter_value)
        for filter_name, filter_value in dict_obj.items()
    })


def _create_value_filter(entity: Any) -> ValueFilter:
    if isinstance(entity, Dict):
        value_filter = __convert_entity_to_value_filter(entity.get(FilterField.VALUE))
        value_filter.operation = entity.get(FilterField.OPERATION, ProtobufDefaults.INT.value)
        value_filter.key = entity.get(FilterField.KEY, ProtobufDefaults.BOOL.value)

        return value_filter

    else:
        return __convert_entity_to_value_filter(entity)


@singledispatch
def __convert_entity_to_value_filter(entity: Any) -> ValueFilter:
    raise TypeError(f'Cannot convert {type(entity)} object to ValueFilter: {entity}')


@__convert_entity_to_value_filter.register(ValueFilter)
def _(value_filter: ValueFilter) -> ValueFilter:
    return value_filter


@__convert_entity_to_value_filter.register(str)
@__convert_entity_to_value_filter.register(int)
@__convert_entity_to_value_filter.register(float)
def _(simple_obj: Union[str, int, float]) -> ValueFilter:
    return ValueFilter(simple_filter=str(simple_obj))


@__convert_entity_to_value_filter.register(list)
def _(list_obj: list) -> ValueFilter:
    if __is_simple_list(list_obj):
        return ValueFilter(simple_list=SimpleList(simple_values=list(map(str, list_obj))))

    elif __is_list_value_filter(list_obj):
        return ValueFilter(list_filter=ListValueFilter(values=list(map(_create_value_filter, list_obj))))

    raise TypeError(f'Expected list to contain strings or dicts: {list_obj}')


@__convert_entity_to_value_filter.register(dict)
def _(dict_obj: dict) -> ValueFilter:
    return ValueFilter(message_filter=dict_to_message_filter(dict_obj))


@__convert_entity_to_value_filter.register(type(None))
def _(none_obj: None) -> ValueFilter:
    return ValueFilter(null_value=NullValue.NULL_VALUE)


def __is_list_value_filter(list_obj: List[Any]) -> bool:
    if all(isinstance(v, dict) for v in list_obj):
        return True

    return False


def __is_simple_list(list_obj: list) -> bool:
    if all(isinstance(v, str) for v in list_obj):
        return True

    return False


# =========================
# MetadataFilter
# =========================

def dict_to_metadata_filter(dict_obj: Dict[str, Any]) -> MetadataFilter:
    return MetadataFilter(property_filters={
        filter_name: _create_simple_filter(filter_value)
        for filter_name, filter_value in dict_obj.items()
    })


@singledispatch
def _create_simple_filter(entity: Any) -> MetadataFilter.SimpleFilter:
    raise TypeError(f'Cannot convert {type(entity)} object to MetadataFilter.SimpleFilter: {entity}')


@_create_simple_filter.register(MetadataFilter.SimpleFilter)
def _(simple_filter: MetadataFilter.SimpleFilter) -> MetadataFilter.SimpleFilter:
    return simple_filter


@_create_simple_filter.register(dict)
def _(dict_obj: dict) -> MetadataFilter.SimpleFilter:
    simple_filter = __convert_entity_to_simple_filter(dict_obj[FilterField.VALUE])

    simple_filter.operation = dict_obj.get(FilterField.OPERATION, ProtobufDefaults.INT.value)
    simple_filter.key = dict_obj.get(FilterField.KEY, ProtobufDefaults.BOOL.value)

    return simple_filter


@singledispatch
def __convert_entity_to_simple_filter(entity: Any) -> MetadataFilter.SimpleFilter:
    raise TypeError(f'Cannot convert {type(entity)} object to MetadataFilter.SimpleFilter: {entity}')


@__convert_entity_to_simple_filter.register(list)
def _(list_obj: list) -> MetadataFilter.SimpleFilter:
    if __is_simple_list(list_obj):
        return MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=list(map(str, list_obj))))

    raise TypeError(f'Expected list to contain strings: {list_obj}')


@__convert_entity_to_simple_filter.register(str)
@__convert_entity_to_simple_filter.register(int)
@__convert_entity_to_simple_filter.register(float)
def _(simple_obj: Union[str, int, float]) -> MetadataFilter.SimpleFilter:
    return MetadataFilter.SimpleFilter(value=str(simple_obj))
