import pyarrow

import sarus_data_spec.protobuf as sp
import sarus_data_spec.type as sdt
import sarus_data_spec.typing as st


def from_arrow(type: pyarrow.DataType) -> sdt.Type:
    # Integers
    if pyarrow.types.is_int32(type):
        return sdt.Integer(base=st.IntegerBase.INT32)
    if pyarrow.types.is_int64(type):
        return sdt.Integer(base=st.IntegerBase.INT64)
    # Floats
    if pyarrow.types.is_float32(type):
        return sdt.Float(base=st.FloatBase.FLOAT32)
    if pyarrow.types.is_float64(type):
        return sdt.Float(base=st.FloatBase.FLOAT64)
    # Text
    if pyarrow.types.is_string(type):
        return sdt.Text()
    if pyarrow.types.is_boolean(type):
        return sdt.Boolean()
    if pyarrow.types.is_date32(type):
        return sdt.Datetime(base=st.DatetimeBase.INT64_NS, format='%Y-%m-%d')
    if pyarrow.types.is_timestamp(type):
        return sdt.Datetime(base=st.DatetimeBase.INT64_NS, format='%Y-%m-%d')
    if pyarrow.types.is_null(type):
        return sdt.Unit()
    raise NotImplementedError('Type not implemented')


def type_from_arrow(arrow_type: pyarrow.DataType, nullable: bool) -> st.Type:
    if nullable and not (pyarrow.types.is_null(arrow_type)):
        return sdt.Optional(type=from_arrow(arrow_type))
    return from_arrow(arrow_type)


def to_arrow(sarus_type: sp.Type, nullable: bool = False) -> pyarrow.DataType:
    """Convert Sarus type to PyArrow type.

    See https://arrow.apache.org/docs/python/api/datatypes.html.
    """
    # Integers
    if sarus_type.HasField("integer"):
        if sarus_type.integer.base == sp.Type.Integer.Base.INT64:
            return pyarrow.int64()
        elif sarus_type.integer.base == sp.Type.Integer.Base.INT32:
            return pyarrow.int32()
        elif sarus_type.integer.base == sp.Type.Integer.Base.INT16:
            return pyarrow.int16()
        elif sarus_type.integer.base == sp.Type.Integer.Base.INT8:
            return pyarrow.int8()

    # Enums
    if sarus_type.HasField("enum"):
        return pyarrow.string()

    # Floats
    elif sarus_type.HasField("float"):
        if sarus_type.float.base == sp.Type.Float.Base.FLOAT64:
            return pyarrow.float64()
        elif sarus_type.float.base == sp.Type.Float.Base.FLOAT32:
            return pyarrow.float32()
        elif sarus_type.float.base == sp.Type.Float.Base.FLOAT16:
            return pyarrow.float16()

    # Bytes
    elif sarus_type.HasField("bytes"):
        return pyarrow.binary()

    # Text
    elif sarus_type.HasField("text"):
        return pyarrow.string()
    # Id
    elif sarus_type.HasField("id"):

        if sarus_type.id.base == sp.Type.Id.Base.INT64:
            return pyarrow.int64()
        elif sarus_type.id.base == sp.Type.Id.Base.INT32:
            return pyarrow.int32()
        elif sarus_type.id.base == sp.Type.Id.Base.INT16:
            return pyarrow.int16()
        elif sarus_type.id.base == sp.Type.Id.Base.INT8:
            return pyarrow.int8()
        elif sarus_type.id.base == sp.Type.Id.Base.STRING:
            return pyarrow.string()
        else:
            return pyarrow.binary()

    # Boolean
    elif sarus_type.HasField("boolean"):
        return pyarrow.bool_()

    # Struct
    elif sarus_type.HasField("struct"):
        fields = sarus_type.struct.fields
        return pyarrow.struct(
            [
                pyarrow.field(
                    name=field.name,
                    type=to_arrow(field.type),
                    nullable=field.type.HasField('optional')
                    or field.type.HasField('unit'),
                )
                for field in fields
            ]
        )

    # Optional
    elif sarus_type.HasField("optional"):
        return to_arrow(sarus_type.optional.type, nullable=True)

    # List
    elif sarus_type.HasField("list"):
        return pyarrow.list_(
            to_arrow(sarus_type.list.type), sarus_type.list.max_size
        )

    # Union
    elif sarus_type.HasField("union"):
        return pyarrow.struct(
            [
                pyarrow.field(
                    name=field.name,
                    type=to_arrow(field.type),
                    nullable=True,
                )
                for field in sarus_type.union.fields
            ]
            + [pyarrow.field(name='field_selected', type=pyarrow.string())]
        )

    # Array
    elif sarus_type.HasField("array"):
        # No real mapping for array in PyArrow
        raise NotImplementedError

    elif sarus_type.HasField('datetime'):
        if sarus_type.datetime.base == sp.Type.Datetime.INT64_NS:
            return pyarrow.timestamp('ns')
        elif sarus_type.datetime.base == sp.Type.Datetime.INT64_MS:
            return pyarrow.timestamp('ms')
        else:
            return pyarrow.string()
    return pyarrow.null()
