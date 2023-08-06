from __future__ import annotations

import typing as t

import pyarrow as pa

from sarus_data_spec.arrow.schema import to_arrow
from sarus_data_spec.base import Referring
from sarus_data_spec.constants import DATASET_SLUGNAME
from sarus_data_spec.path import Path, path
from sarus_data_spec.type import Type
import sarus_data_spec.dataset as sd
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


class Schema(Referring[sp.Schema]):
    """A python class to describe schemas"""

    def __init__(self, protobuf: sp.Schema) -> None:
        self._referred = {
            protobuf.dataset
        }  # This has to be defined before it is initialized
        super().__init__(protobuf)

    def prototype(self) -> t.Type[sp.Schema]:
        """Return the type of the underlying protobuf."""
        return sp.Schema

    def name(self) -> str:
        return self._protobuf.name

    def dataset(self) -> sd.Dataset:
        return t.cast(
            sd.Dataset, self.storage().referrable(self._protobuf.dataset)
        )

    def to_arrow(self) -> pa.Schema:
        return to_arrow(self.protobuf())

    def type(self) -> Type:
        """Returns the first type level of the schema"""
        return Type(self.protobuf().type)

    def protected_path(self) -> Path:
        """Returns the path to the protected entities"""
        return Path(self.protobuf().protected)

    def data_type(self) -> Type:
        """Returns the first type level containing the data,
        hence skips the protected_entity struct if there is one"""
        type = self.protobuf().type
        if type.HasField('struct'):
            keys = [
                i
                for i, element in enumerate(type.struct.fields)
                if element.name == 'data'
            ]
            if len(keys) > 0:
                assert len(keys) == 1
                return Type(type.struct.fields[keys[0]].type)
        return Type(type)

    # TODO: Add to_parquet, to_tensorflow, to_sql... here?
    # The Schema has a manager, it would provide the implementation

    def tables(self) -> t.List[st.Path]:
        struct_paths = self.data_type().structs()
        if struct_paths is None:  # there is no struct
            return []
        if len(struct_paths) == 0:  # struct is the first level
            return [path(label='data')]
        return [
            path(label='data', paths=[t.cast(Path, element)])
            for element in struct_paths
        ]


# Builder
def schema(
    dataset: st.Dataset,
    fields: t.Optional[t.Mapping[str, st.Type]] = None,
    schema_type: t.Optional[st.Type] = None,
    protected_paths: t.Optional[sp.Path] = None,
    properties: t.Optional[t.Mapping[str, str]] = None,
    name: t.Optional[str] = None,
) -> Schema:
    """A builder to ease the construction of a schema"""
    if name is None:
        name = dataset.properties().get(
            DATASET_SLUGNAME, f'{dataset.name()}_schema'
        )
    assert name is not None

    if fields is not None:
        return Schema(
            sp.Schema(
                dataset=dataset.uuid(),
                name=name,
                type=sp.Type(
                    struct=sp.Type.Struct(
                        fields=[
                            sp.Type.Struct.Field(
                                name=name, type=type.protobuf()
                            )
                            for name, type in fields.items()
                        ]
                    )
                ),
                protected=protected_paths,
                properties=properties,
            )
        )
    if schema_type is not None:
        return Schema(
            sp.Schema(
                dataset=dataset.uuid(),
                name=name,
                type=schema_type.protobuf(),
                protected=protected_paths,
                properties=properties,
            )
        )
    # If none of fields or type is defined, set type to Null
    return Schema(
        sp.Schema(
            dataset=dataset.uuid(),
            name=name,
            type=sp.Type(name='Null', null=sp.Type.Null()),
            protected=protected_paths,
            properties=properties,
        )
    )


if t.TYPE_CHECKING:
    test_schema: st.Schema = schema(sd.sql(uri='sqlite:///:memory:'))
