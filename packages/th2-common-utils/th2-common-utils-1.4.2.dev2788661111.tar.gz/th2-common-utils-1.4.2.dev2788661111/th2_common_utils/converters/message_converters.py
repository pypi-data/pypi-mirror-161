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

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from google.protobuf.json_format import ParseDict
from th2_common_utils.util.tree_table import Table, TreeTable
from th2_grpc_common.common_pb2 import ConnectionID, Direction, EventID, ListValue, Message, MessageID, \
    MessageMetadata, Value

DictMessageType = Union[str, List, Dict]


def _message_to_dict_convert_value(value: Value) -> Optional[DictMessageType]:
    value_kind = value.WhichOneof('kind')

    if value_kind == 'simple_value':
        return value.simple_value  # type: ignore

    elif value_kind == 'list_value':
        return list(map(_message_to_dict_convert_value, value.list_value.values))

    elif value_kind == 'message_value':
        return {
            field: _message_to_dict_convert_value(field_value)
            for field, field_value in value.message_value.fields.items()
        }

    else:
        raise TypeError(f'Expected simple_value, list_value or message_value. {type(value)} object received: {value}')


def message_to_dict(message: Message) -> Dict[str, Optional[DictMessageType]]:
    """Converts th2-message to a dict.
    Fields of th2-message will be converted to a dict. You will lose all metadata.
    Args:
        message: th2-message.
    Returns:
        th2-message fields (message.fields) as a dict. All nested entities will be also converted.
        Conversion rules:
            Value.simple_value - str
            Value.list_value - list
            Value.message_value - dict
    Raises:
        TypeError: Occurs when 'message.fields' contains a field not of the 'Value' type.
    """
    message_metadata = message.metadata

    return {
        'parent_event_id': message.parent_event_id.id,
        'metadata': {
            'session_alias': message_metadata.id.connection_id.session_alias,
            'session_group': message_metadata.id.connection_id.session_group,
            'direction': Direction.Name(message_metadata.id.direction),
            'sequence': message_metadata.id.sequence,
            'subsequence': list(message_metadata.id.subsequence),
            'timestamp': message_metadata.timestamp.ToDatetime() if message_metadata.HasField('timestamp') else None,
            'message_type': message_metadata.message_type,
            'properties': {k: v for k, v in message_metadata.properties.items()},
            'protocol': message_metadata.protocol
        },
        'fields': {
            field: _message_to_dict_convert_value(field_value)
            for field, field_value in message.fields.items()
        }
    }


def _dict_to_message_convert_value(entity: Any) -> Value:
    if isinstance(entity, (str, int, float)):
        return Value(simple_value=str(entity))
    elif isinstance(entity, list):
        return Value(list_value=ListValue(values=list(map(_dict_to_message_convert_value, entity))))
    elif isinstance(entity, dict):
        return Value(message_value=Message(fields={k: _dict_to_message_convert_value(v) for k, v in entity.items()}))

    elif isinstance(entity, Value):
        return entity
    elif isinstance(entity, ListValue):
        return Value(list_value=entity)
    elif isinstance(entity, Message):
        return Value(message_value=entity)

    else:
        raise TypeError(f'Cannot convert {type(entity)} object.')


def dict_to_message(fields: dict,
                    parent_event_id: Optional[EventID] = None,
                    session_alias: str = '',
                    message_type: str = '') -> Message:
    """Converts a dict to th2-message with 'metadata' and 'parent_event_id'.
    Args:
        fields: Message fields as a dict.
        parent_event_id: Parent event id.
        session_alias: Session alias (is used when creating message metadata).
        message_type: Message type (is used when creating message metadata).
    Returns:
        th2-message with 'metadata' and 'parent_event_id'. All 'fields' nested entities will be converted.
        Conversion rules:
            str, int, float, Value - Value.simple_value
            list, ListValue - Value.list_value
            dict, Message - Value.message_value.
    Raises:
        TypeError: Occurs when 'message.fields' contains a field of the unsupported type.
    """

    if parent_event_id is None:
        parent_event_id = EventID()

    return Message(parent_event_id=parent_event_id,
                   metadata=MessageMetadata(id=MessageID(connection_id=ConnectionID(session_alias=session_alias)),
                                            message_type=message_type),
                   fields={field: _dict_to_message_convert_value(field_value) for field, field_value in fields.items()})


def _message_to_table_convert_value(message_value: Union[str, List, Dict],
                                    columns_names: List[str]) -> Optional[Union[str, Table]]:
    if isinstance(message_value, str):
        return message_value  # type: ignore

    elif isinstance(message_value, list):
        table = Table(columns_names)

        for index, list_item in enumerate(message_value):
            table_inner_item = _message_to_table_convert_value(list_item, columns_names)
            if isinstance(table_inner_item, Table):
                table.add_table(index, table_inner_item)
            else:
                table.add_row(index, table_inner_item)

        return table

    elif isinstance(message_value, dict):
        table = Table(columns_names)

        for field_name, field_value in message_value.items():  # type: ignore
            table_inner_item = _message_to_table_convert_value(field_value, columns_names)
            if isinstance(table_inner_item, Table):
                table.add_table(field_name, table_inner_item)
            else:
                table.add_row(field_name, table_inner_item)

        return table

    else:
        raise TypeError(f'Expected object type of str, int, float, list or dict, got {type(message_value)}')


def message_to_table(message: Union[Dict, Message]) -> TreeTable:
    """Converts th2-message or dict to a TreeTable.
    Table can have only two columns. Nested tables are allowed. You will lose 'parent_event_id' and 'metadata'
    of the message.
    Args:
        message: th2-message.
    Returns:
        Tree table with two columns - one contains the name of the field and the other contains the value of this field.
    Raises:
        TypeError: Occurs when 'message.fields' contains a field not of the 'Value' type.
    """

    if isinstance(message, Message):
        message = message_to_dict(message)['fields']  # type: ignore

    table = TreeTable(columns_names=['Field Value'])

    for field_name in message:  # type: ignore
        table_entity = _message_to_table_convert_value(message[field_name], table.columns_names)  # type: ignore
        if isinstance(table_entity, Table):
            table.add_table(field_name, table_entity)
        else:
            table.add_row(field_name, table_entity)

    return table


def json_to_message(json_path: Union[str, Path]) -> Message:
    """Read json file and convert its content to th2-message.
    Args:
        json_path: Path to json file.
    Returns:
        th2-message
    """

    with open(json_path, 'r') as read_content:
        json_dict = json.load(read_content)

    return ParseDict(json_dict, Message())
