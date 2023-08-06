from typing import Any, AsyncIterator, cast
import json
import typing as t

import pyarrow as pa

from sarus_data_spec.constants import DATASET_SLUGNAME
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.path import Path, path
from sarus_data_spec.protobuf.typing import Protobuf
from sarus_data_spec.protobuf.utilities import from_base64, to_base64
from sarus_data_spec.schema import schema
import sarus_data_spec.protobuf as sp
import sarus_data_spec.type as sdt
import sarus_data_spec.typing as st

from .external.routing import arrow_external, external
from .standard.filter import filter_to_arrow
from .standard.get_item import get_item_to_arrow
from .standard.project import project_to_arrow
from .standard.sample import arrow_sample


async def transformed_dataset_arrow(
    dataset: st.Dataset, batch_size: int
) -> AsyncIterator[pa.RecordBatch]:
    """Routes a transformed Dataspec to its Arrow implementation."""
    transform = dataset.transform()
    if transform.is_external():
        return await arrow_external(dataset, batch_size)
    elif transform.protobuf().spec.HasField('sample'):
        return await arrow_sample(dataset, batch_size)
    elif transform.protobuf().spec.HasField('filter'):
        return await filter_to_arrow(dataset, batch_size)
    elif transform.protobuf().spec.HasField('project'):
        return await project_to_arrow(dataset, batch_size)
    elif transform.protobuf().spec.HasField('get_item'):
        return await get_item_to_arrow(dataset, batch_size)

    else:
        raise NotImplementedError(
            f"{transform.protobuf().spec.WhichOneof('spec')}"
        )


async def transformed_scalar(scalar: st.Scalar) -> Any:
    """Routes a transformed Scalar to its implementation.

    For now, transformed Scalars are only obtained from external ops. By
    external ops, we mean functions defined in external libraries.
    """
    if scalar.transform().is_external():
        return await external(scalar)
    else:
        raise NotImplementedError(
            f"scalar_transformed for {scalar.transform()}"
        )


def transformed_schema(dataset: st.Dataset) -> st.Schema:
    previous_ds_id = dataset.protobuf().spec.transformed.arguments[
        0
    ]  # how this works?
    previous_schema = cast(
        Dataset, dataset.storage().referrable(previous_ds_id)
    ).schema()
    if dataset.transform().protobuf().spec.HasField('filter'):
        new_type = sdt.Type(dataset.transform().protobuf().spec.filter.filter)
        new_type = update_fks(
            curr_type=new_type, original_type=new_type  # type:ignore
        )
        old_properties = previous_schema.properties()

        if 'primary_keys' in old_properties.keys():
            new_pks = filter_primary_keys(
                old_properties['primary_keys'],
                new_type,
            )
            old_properties['primary_keys'] = new_pks  # type:ignore

        # VERY UGLY SHOULD BE REMOVED WHEN WE HAVE PROTECTED TYPE
        previous_fields = previous_schema.type().children()
        if 'data' in previous_fields.keys():
            previous_fields['data'] = new_type
            new_type = sdt.Struct(fields=previous_fields)
        return schema(
            dataset,
            schema_type=new_type,
            protected_paths=previous_schema.protobuf().protected,
            properties=old_properties,
            name=dataset.properties().get(DATASET_SLUGNAME, None),
        )

    if dataset.transform().protobuf().spec.HasField('get_item'):
        path = Path(dataset.transform().protobuf().spec.get_item.path)
        sub_types = previous_schema.data_type().sub_types(path)
        assert len(sub_types) == 1
        new_type = sub_types[0]  # type:ignore
        # TODO: update foreign_keys/primary_keys in the type
        previous_fields = previous_schema.type().children()
        if 'data' in previous_fields.keys():
            previous_fields['data'] = new_type
            new_type = sdt.Struct(fields=previous_fields)
        return schema(
            dataset,
            schema_type=new_type,
            protected_paths=previous_schema.protobuf().protected,
            name=dataset.properties().get(DATASET_SLUGNAME, None),
        )

    elif dataset.transform().protobuf().spec.HasField(
        'shuffle'
    ) or dataset.transform().protobuf().spec.HasField('sample'):
        return schema(
            dataset,
            schema_type=sdt.Type(previous_schema.protobuf().type),
            protected_paths=previous_schema.protobuf().protected,
            properties=previous_schema.properties(),
            name=dataset.properties().get(DATASET_SLUGNAME, None),
        )

    raise ValueError('Other spec not implemented yet')


def filter_primary_keys(old_pks: str, new_type: st.Type) -> str:
    """Keeps only primary keys path that appear in new type"""
    filtered_pks = []
    primary_keys = [
        Path(cast(sp.Path, from_base64(proto, cast(Protobuf, sp.Path))))
        for proto in json.loads(old_pks)
    ]
    for primary_key in primary_keys:
        try:
            new_type.get(primary_key)
        except KeyError:
            pass

        else:
            filtered_pks.append(to_base64(primary_key.protobuf()))
    return json.dumps(filtered_pks)


def update_fks(curr_type: st.Type, original_type: st.Type) -> st.Type:
    class Select(st.TypeVisitor):
        result = curr_type

        def Struct(
            self,
            fields: t.Mapping[str, st.Type],
            name: t.Optional[str] = None,
        ) -> None:
            new_fields = {}
            for fieldname, fieldtype in fields.items():
                new_fields[fieldname] = update_fks(
                    curr_type=fieldtype, original_type=original_type
                )

            self.result = sdt.Struct(
                fields=new_fields,
                name=name if name is not None else 'Struct',
                properties=curr_type.properties(),
            )
            # otherwise struct is empty and it is a terminal node

        def Union(
            self,
            fields: t.Mapping[str, st.Type],
            name: t.Optional[str] = None,
        ) -> None:
            new_fields = {}
            for fieldname, fieldtype in fields.items():
                new_fields[fieldname] = update_fks(
                    curr_type=fieldtype, original_type=original_type
                )

            self.result = sdt.Union(
                fields=new_fields,
                name=name if name is not None else 'Union',
                properties=curr_type.properties(),
            )

        def Optional(
            self, type: st.Type, name: t.Optional[str] = None
        ) -> None:

            self.result = sdt.Optional(
                type=update_fks(curr_type=type, original_type=original_type),
                name=name if name is not None else 'Optional',
                properties=curr_type.properties(),
            )

        def List(
            self,
            type: st.Type,
            max_size: int,
            name: t.Optional[str] = None,
        ) -> None:
            self.result = sdt.List(
                type=update_fks(curr_type=type, original_type=original_type),
                max_size=max_size,
                name=name if name is not None else 'Optional',
                properties=curr_type.properties(),
            )

        def Array(
            self,
            type: st.Type,
            shape: t.Tuple[int, ...],
            name: t.Optional[str] = None,
        ) -> None:
            self.result = sdt.Array(
                type=update_fks(curr_type=type, original_type=original_type),
                shape=shape,
                name=name if name is not None else 'Optional',
                properties=curr_type.properties(),
            )

        def Id(
            self,
            unique: bool,
            reference: t.Optional[st.Path] = None,
            base: t.Optional[st.IdBase] = None,
        ) -> None:
            if reference is not None:
                try:
                    original_type.get(path(paths=[reference]))
                except KeyError:
                    self.result = sdt.Id(unique=unique, base=base)

    visitor = Select()
    curr_type.accept(visitor)
    return visitor.result
