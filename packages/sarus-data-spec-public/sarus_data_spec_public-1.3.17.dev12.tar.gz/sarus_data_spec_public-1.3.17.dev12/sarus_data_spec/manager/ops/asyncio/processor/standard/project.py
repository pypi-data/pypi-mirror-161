import typing as t

import pyarrow as pa

from sarus_data_spec.arrow.array import convert_record_batch
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.manager.ops.asyncio.processor.standard.filter import (  # noqa : E501
    update_fks,
)
from sarus_data_spec.manager.ops.asyncio.processor.standard.visitor_selector import (  # noqa : E501
    select_columns,
)
import sarus_data_spec.type as sdt
import sarus_data_spec.typing as st


async def project_to_arrow(
    dataset: st.Dataset, batch_size: int
) -> t.AsyncIterator[pa.RecordBatch]:

    previous_ds_id = dataset.protobuf().spec.transformed.arguments[0]
    previous_ds = t.cast(Dataset, dataset.storage().referrable(previous_ds_id))

    parent_schema = previous_ds.schema()
    data_type = sdt.Type(
        dataset.transform().protobuf().spec.project.projection
    )
    data_type = update_fks(
        curr_type=data_type, original_type=parent_schema.type()  # type:ignore
    )

    async def async_generator(
        parent_iter: t.AsyncIterator[pa.RecordBatch],
    ) -> t.AsyncIterator[pa.RecordBatch]:
        async for batch in parent_iter:
            updated_array = select_columns(
                data_type,
                convert_record_batch(
                    record_batch=batch, _type=parent_schema.type()
                ),
            )
            yield pa.RecordBatch.from_struct_array(updated_array)

    return async_generator(
        parent_iter=await previous_ds.async_to_arrow(batch_size=batch_size)
    )
