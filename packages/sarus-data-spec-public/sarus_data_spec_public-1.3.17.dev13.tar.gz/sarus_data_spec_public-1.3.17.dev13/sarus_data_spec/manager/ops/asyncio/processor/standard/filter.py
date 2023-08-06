import typing as t

import pyarrow as pa

from sarus_data_spec.arrow.array import convert_record_batch
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.manager.ops.asyncio.processor.standard.visitor_selector import (  # noqa : E501
    select_rows,
)
from sarus_data_spec.path import path
import sarus_data_spec.type as sdt
import sarus_data_spec.typing as st


async def filter_to_arrow(
    dataset: st.Dataset, batch_size: int
) -> t.AsyncIterator[pa.RecordBatch]:

    previous_ds_id = dataset.protobuf().spec.transformed.arguments[0]
    previous_ds = t.cast(Dataset, dataset.storage().referrable(previous_ds_id))
    parent_schema = previous_ds.schema()
    data_type = sdt.Type(dataset.transform().protobuf().spec.filter.filter)
    data_type = update_fks(
        curr_type=data_type, original_type=parent_schema.type()  # type:ignore
    )

    async def async_generator(
        parent_iter: t.AsyncIterator[pa.RecordBatch],
    ) -> t.AsyncIterator[pa.RecordBatch]:
        async for batch in parent_iter:
            # TODO: what follows is really ugly and is necessary
            # because we do not have a proper type for the
            # protected entity, it will be removed when we
            # switch to that formalism
            array = convert_record_batch(
                record_batch=batch, _type=parent_schema.type()
            )
            if 'data' in previous_ds.schema().type().children():
                old_arrays = array.flatten()
                array = array.field('data')
                updated_array, filter_indices = select_rows(
                    dataset.schema().data_type(),
                    array,
                )
                old_arrays[0] = updated_array
                new_struct = pa.StructArray.from_arrays(
                    old_arrays,
                    names=list(previous_ds.schema().type().children().keys()),
                )
                yield pa.RecordBatch.from_struct_array(
                    new_struct.filter(filter_indices)
                )
            else:
                updated_array, filter_indices = select_rows(
                    dataset.schema().data_type(),
                    array,
                )
                yield pa.RecordBatch.from_struct_array(
                    updated_array.filter(filter_indices)
                )

            updated_array, filter_indices = select_rows(
                data_type,
                convert_record_batch(
                    record_batch=batch, _type=parent_schema.type()
                ),
            )
            yield pa.RecordBatch.from_struct_array(
                updated_array.filter(filter_indices)
            )

    return async_generator(
        parent_iter=await previous_ds.async_to_arrow(batch_size=batch_size)
    )


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
