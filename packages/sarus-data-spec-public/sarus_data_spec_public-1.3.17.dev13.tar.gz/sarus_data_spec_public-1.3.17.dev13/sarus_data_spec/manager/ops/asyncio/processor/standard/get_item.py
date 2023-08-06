import typing

import pyarrow as pa

from sarus_data_spec.arrow.array import convert_record_batch
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.manager.ops.asyncio.processor.standard.visitor_selector import (  # noqa : E501
    select_rows,
)
from sarus_data_spec.path import Path
import sarus_data_spec.typing as st


async def get_item_to_arrow(
    dataset: st.Dataset, batch_size: int
) -> typing.AsyncIterator[pa.RecordBatch]:

    previous_ds_id = dataset.protobuf().spec.transformed.arguments[0]
    previous_ds = typing.cast(
        Dataset, dataset.storage().referrable(previous_ds_id)
    )
    path = Path(dataset.transform().protobuf().spec.get_item.path)
    parent_schema = previous_ds.schema()

    async def async_generator(
        parent_iter: typing.AsyncIterator[pa.RecordBatch],
    ) -> typing.AsyncIterator[pa.RecordBatch]:
        async for batch in parent_iter:
            # TODO: what follows is really ugly and is necessary
            # because we do not have a proper type for the
            # protected entity, it will be removed when we
            # switch to that formalism
            array = convert_record_batch(
                record_batch=batch, _type=parent_schema.type()
            )
            array = convert_record_batch(
                record_batch=batch, _type=previous_ds.schema().type()
            )
            # VERY UGLY SHOULD BE REMOVED WHEN WE HAVE PROTECTED TYPE
            if 'data' in previous_ds.schema().type().children():
                old_arrays = array.flatten()
                array = array.field('data')
                updated_array = get_items(
                    _type=previous_ds.schema().data_type(),
                    array=array,
                    path=path,
                )
                old_arrays[0] = updated_array
                new_struct = pa.StructArray.from_arrays(
                    old_arrays,
                    names=list(previous_ds.schema().type().children().keys()),
                )
                yield pa.RecordBatch.from_struct_array(new_struct)
            else:
                updated_array = get_items(
                    _type=previous_ds.schema().data_type(),
                    array=array,
                    path=path,
                )
                if isinstance(updated_array, pa.StructArray):
                    yield pa.RecordBatch.from_struct_array(updated_array)
                else:
                    yield pa.RecordBatch.from_arrays(
                        [updated_array], names=[path.to_strings_list()[0][-1]]
                    )

    return async_generator(
        parent_iter=await previous_ds.async_to_arrow(batch_size=batch_size)
    )


def get_items(array: pa.Array, path: st.Path, _type: st.Type) -> pa.Array:
    """Visitor selecting columns based on the type.
    The idea is that at each level,
    the filter for the array is computed, and for the union,
    we remove the fields that we want to filter among
    the columns
    """

    class ItemSelector(st.TypeVisitor):
        batch_array: pa.Array = array

        def Struct(
            self,
            fields: typing.Mapping[str, st.Type],
            name: typing.Optional[str] = None,
        ) -> None:

            if len(path.sub_paths()) > 0:
                sub_path = path.sub_paths()[0]
                self.batch_array = get_items(
                    array=array.field(sub_path.label()),
                    path=sub_path,
                    _type=fields[sub_path.label()],
                )

        def Constrained(
            self,
            type: st.Type,
            constraint: st.Predicate,
            name: typing.Optional[str] = None,
        ) -> None:
            raise NotImplementedError

        def Optional(
            self, type: st.Type, name: typing.Optional[str] = None
        ) -> None:
            array = self.batch_array.field(path.label())
            if len(path.sub_paths()) == 0:
                self.batch_array = array
            else:
                self.batch_array = get_items(
                    array=array, path=path.sub_paths()[0], _type=type
                )

        def Union(
            self,
            fields: typing.Mapping[str, st.Type],
            name: typing.Optional[str] = None,
        ) -> None:

            if len(path.sub_paths()) == 0:
                self.batch_array = array
            else:
                sub_path = path.sub_paths()[0]
                self.batch_array = get_items(
                    array=array.field(sub_path.label()),
                    path=sub_path,
                    _type=fields[sub_path.label()],
                )

        def Array(
            self,
            type: st.Type,
            shape: typing.Tuple[int, ...],
            name: typing.Optional[str] = None,
        ) -> None:
            raise NotImplementedError

        def List(
            self,
            type: st.Type,
            max_size: int,
            name: typing.Optional[str] = None,
        ) -> None:
            raise NotImplementedError

    visitor = ItemSelector()
    _type.accept(visitor)
    return visitor.batch_array
