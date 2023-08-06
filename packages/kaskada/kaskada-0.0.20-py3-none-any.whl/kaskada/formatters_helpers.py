"""
Copyright (C) 2022 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from datetime import datetime
from domonic.html import b, pre, td, tr
import pandas
import re

import kaskada.fenl.v1alpha as kaskada_fenl_pb2

'''
NOTES:

Use `hasattr(obj, prop) to test if an object has a property`
Use `obj.HasField(prop) to test if an object has a specific one-of`
'''

kaskada_fenl_primitive_types = {
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_BOOL: "bool",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_DURATION_MICROSECOND: "duration_us",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_DURATION_MILLISECOND: "duration_ms",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_DURATION_NANOSECOND: "duration_ns",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_DURATION_SECOND: "duration_s",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_F16: "f16",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_F32: "f32",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_F64: "f64",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_I16: "i16",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_I32: "i32",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_I64: "i64",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_I8: "i8",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_INTERVAL_DAY_TIME: "interval_days",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_INTERVAL_YEAR_MONTH: "interval_months",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_NULL: "null",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_STRING: "string",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_TIMESTAMP_MICROSECOND: "timestamp_us",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_TIMESTAMP_MILLISECOND: "timestamp_ms",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_TIMESTAMP_NANOSECOND: "timestamp_ns",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_TIMESTAMP_SECOND: "timestamp_s",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_U16: "u16",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_U32: "u32",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_U64: "u64",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_U8: "u8",
}


def get_item(obj, keys, default=""):
    """
    Safely recursively gets an item from a dict, otherwise returns the default value

    Args:
        obj (dict of {str : Any}): Dictionary of (nested) key item pairs
        keys (list of str): The list of keys use to navigate to the desired item in the dictionary.
        default (str, optional): The default value to return if the item isn't found. Defaults to "".

    Returns:
        string: Either the found value or the default.
    """
    while len(keys) > 0:
        key = keys.pop(0)
        if key in obj:
            obj = obj[key]
        else:
            return default
    return obj


def appendChildIfNotNone(parent, child):
    if child is not None:
        parent.appendChild(child)


def appendChildren(parent, children):
    for child in children:
        appendChildIfNotNone(parent, child)


def html_obj_table_row(key, value):
    """
    Returns a html table row, where the key is bolded, and the value is output as code.
    """
    if value is None or value == "":
        return None
    return tr(td(b(key)), td(pre(value)))


def html_table_row(key, value):
    """
    Returns a html table row, where the key is bolded, and the value is output as is.
    """
    return tr(td(b(key)), td(value))


def html_obj_id_row(index, obj, props):
    obj_type = type(obj).__name__.lower()
    obj_name_key = f"{obj_type}_name"
    obj_name = get_item(props, [obj_name_key])
    return tr(td(pre(index)), td(pre(obj_name)))


def appendHtmlObjTableRowIfAttrExists(parent, obj, attr):
    if hasattr(obj, attr):
        parent.appendChild(html_obj_table_row(attr, getattr(obj, attr)))


def appendHtmlObjTableRowIfHasField(parent, obj, field):
    if obj.HasField(field):
        parent.appendChild(html_obj_table_row(field, getattr(obj, field)))


def convert_fenl_schema_field(field):
    """
    Converts a fenl field to a string representation.

    Args:
        field (kaskada_fenl_pb2.schema_pb2.Schema_Field) : the input field

    Returns:
        str: The string representation of the fenl Field
    """
    return field.name, convert_fenl_datatype(field.data_type)


def convert_fenl_datatype(data_type):
    """
    Converts a fenl dataType to a string representation.

    Args:
        data_type (kaskada_fenl_pb2.schema_pb2.DataType) : the input dataType

    Returns:
        str: The string representation of the fenl DataType
    """
    type_string = None
    if data_type.HasField("primitive"):
        type_string = kaskada_fenl_primitive_types.get(data_type.primitive, "<unknown>")
    elif data_type.HasField("struct"):
        type_string = "<struct>"
    elif data_type.HasField("window"):
        type_string = "<window>"
    return type_string


def get_schema_dataframe(obj):
    """
    Gets a dataframe from a schema object if it exists

    Args:
        obj (kaskada.fenl.v1alpha.schema_pb2.Schema | Any):
            Either a schema object or an object that has a schema or analysis object at the root level

    Returns:
        pandas.dataframe | None:
            Either a dataframe describing the schemea or None if no schema exists in the passed object.
    """
    if hasattr(obj, "schema"):
        obj = obj.schema

    if (not hasattr(obj, "fields")) or len(obj.fields) == 0:
        return None
    fields = {}
    for idx, field in enumerate(obj.fields):
        name, typeString = convert_fenl_schema_field(field)
        fields[idx] = [name, typeString]
    return pandas.DataFrame.from_dict(
        data=fields, orient="index", columns=["column_name", "column_type"]
    )


def get_datetime(pb2_timestamp):
    """
    Converts a google.protobuf.timestamp_pb2 into a python datetime object.

    Args:
        pb2_timestamp (google.protobuf.timestamp_pb2): The protobuf timestamp.

    Returns:
        datetime: The python datetime.
    """
    return datetime.fromtimestamp(pb2_timestamp.seconds + pb2_timestamp.nanos / 1e9)


def get_classname(obj):
    return f"{obj.__module__}.{obj.__name__}"


def get_properties(obj):
    """
    Converts a protobuf response into a simple python dictionary.

    Args:
        obj (Any): A deserialized protobuf object.

    Returns:
        dict of {str : Any}: A nested set of keys and values with structure matching the protobuf input.
    """
    results = {}
    for propName in dir(obj):
        if re.search(r"^[a-z]", propName) is None:
            continue
        propVal = getattr(obj, propName)
        propType = type(propVal)
        prop_class = get_classname(propType)
        if propType.__name__ in ("method"):
            continue
        elif propType in (int, float, bool):
            results[propName] = propVal
        elif propType is str:
            if propVal != "":
                results[propName] = propVal
        elif prop_class == "google.protobuf.pyext._message.RepeatedCompositeContainer":
            if len(propVal) > 0:
                results[propName] = [get_properties(subObj) for subObj in propVal]
        elif prop_class == "google.protobuf.timestamp_pb2.Timestamp":
            results[propName] = get_datetime(propVal).isoformat()
        elif prop_class.startswith("pandas."):
            results[propName] = propVal
        else:
            results[propName] = get_properties(propVal)
    return results
