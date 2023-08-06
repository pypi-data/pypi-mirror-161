from __future__ import annotations

import hashlib
import json
import os
import typing as t
import warnings

import pandas as pd
import pyarrow as pa

try:
    import tensorflow as tf
except ModuleNotFoundError:
    pass  # Warning is displayed by typing.py

from uuid import UUID

from sarus_data_spec.attribute import attach_properties
from sarus_data_spec.constants import (
    BIG_DATA_TASK,
    BIG_DATA_THRESHOLD,
    DATASET_N_BYTES,
    DATASET_N_LINES,
    IS_BIG_DATA,
    THRESHOLD_TYPE,
)
from sarus_data_spec.protobuf.utilities import copy
from sarus_data_spec.protobuf.utilities import json as utilities_json
from sarus_data_spec.protobuf.utilities import serialize, type_name
from sarus_data_spec.query_manager.base import BaseQueryManager
import sarus_data_spec.manager.typing as manager_typing
import sarus_data_spec.protobuf as sp
import sarus_data_spec.status as stt
import sarus_data_spec.storage.typing as storage_typing
import sarus_data_spec.typing as st


class Base(manager_typing.Manager):
    """Provide the dataset functionalities."""

    def __init__(
        self, storage: storage_typing.Storage, protobuf: sp.Manager
    ) -> None:
        self._protobuf: sp.Manager = copy(protobuf)
        self._freeze()
        self._storage = storage
        self.storage().store(self)
        self._parquet_dir = os.path.expanduser('/tmp/sarus_dataset/')
        os.makedirs(self.parquet_dir(), exist_ok=True)
        self.query_manager = BaseQueryManager(storage=storage)

    def parquet_dir(self) -> str:
        return self._parquet_dir

    def protobuf(self) -> sp.Manager:
        return copy(self._protobuf)

    def prototype(self) -> t.Type[sp.Manager]:
        return sp.Manager

    def type_name(self) -> str:
        return type_name(self._protobuf)

    def __repr__(self) -> str:
        return utilities_json(self._protobuf)

    def __getitem__(self, key: str) -> str:
        return t.cast(str, self._protobuf.properties[key])

    def properties(self) -> t.Mapping[str, str]:
        return self.protobuf().properties

    def _checksum(self) -> bytes:
        """Compute an md5 checksum"""
        md5 = hashlib.md5()
        md5.update(serialize(self._protobuf))
        return md5.digest()

    def _freeze(self) -> None:
        self._protobuf.uuid = ''
        self._frozen_checksum = self._checksum()
        self._protobuf.uuid = UUID(bytes=self._frozen_checksum).hex

    def _frozen(self) -> bool:
        uuid = self._protobuf.uuid
        self._protobuf.uuid = ''
        result = (self._checksum() == self._frozen_checksum) and (
            uuid == UUID(bytes=self._frozen_checksum).hex
        )
        self._protobuf.uuid = uuid
        return result

    def uuid(self) -> str:
        return self._protobuf.uuid

    def referring(
        self, type_name: t.Optional[str] = None
    ) -> t.Collection[st.Referring]:
        return self.storage().referring(self, type_name=type_name)

    def storage(self) -> storage_typing.Storage:
        return self._storage

    def schema(self, dataset: st.Dataset) -> st.Schema:
        raise NotImplementedError

    def marginals(self, dataset: st.Dataset) -> st.Marginals:
        raise NotImplementedError

    def size(self, dataset: st.Dataset) -> st.Size:
        raise NotImplementedError

    def is_compliant(
        self,
        dataspec: st.DataSpec,
        kind: st.ConstraintKind,
        public_context: t.List[str],
        epsilon: t.Optional[float],
    ) -> bool:
        return self.query_manager.is_compliant(
            dataspec,
            kind=kind,
            public_context=public_context,
            epsilon=epsilon,
        )

    def variant(
        self,
        dataspec: st.DataSpec,
        kind: st.ConstraintKind,
        public_context: t.List[str],
        epsilon: t.Optional[float],
    ) -> t.Optional[st.DataSpec]:
        return self.query_manager.variant(
            dataspec=dataspec,
            kind=kind,
            public_context=public_context,
            epsilon=epsilon,
        )

    def variants(self, dataspec: st.DataSpec) -> t.Collection[st.DataSpec]:
        return self.query_manager.variants(dataspec=dataspec)

    def variant_constraint(
        self, dataspec: st.DataSpec
    ) -> t.Optional[st.VariantConstraint]:
        return self.query_manager.variant_constraint(dataspec)

    def set_remote(self, dataspec: st.DataSpec) -> None:
        """Add an Attribute to tag the DataSpec as remotely fetched."""
        attach_properties(dataspec, {"is_remote": str(True)})

    def is_remote(self, dataspec: st.DataSpec) -> bool:
        """Is the dataspec a remotely defined dataset."""
        attributes = self.storage().referring(
            dataspec, type_name=sp.type_name(sp.Attribute)
        )
        is_remote = [
            att.properties()["is_remote"]
            for att in attributes
            if "is_remote" in att.properties()
        ]
        return str(True) in is_remote

    def infer_output_type(
        self,
        transform: st.Transform,
        *arguments: st.DataSpec,
        **named_arguments: st.DataSpec,
    ) -> t.Tuple[str, t.Callable[[st.DataSpec], None]]:
        """Infer the transform output type : minimal type inference."""

        def attach_nothing(ds: st.DataSpec) -> None:
            return

        if not transform.is_external():
            # By default, results of non external transforms (e.g. join,
            # sample) are Datasets and non external transforms are only applied
            # to Datasets

            return sp.type_name(sp.Dataset), attach_nothing

        return sp.type_name(sp.Scalar), attach_nothing

    def verifies(
        self,
        variant_constraint: st.VariantConstraint,
        kind: st.ConstraintKind,
        public_context: t.Collection[str],
        epsilon: t.Optional[float],
    ) -> bool:
        return self.query_manager.verifies(
            variant_constraint=variant_constraint,
            kind=kind,
            public_context=public_context,
            epsilon=epsilon,
        )

    def bounds(self, dataset: st.Dataset) -> st.Bounds:
        raise NotImplementedError

    def to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> t.Iterator[pa.RecordBatch]:
        raise NotImplementedError

    def to_pandas(self, dataset: st.Dataset) -> pd.DataFrame:
        raise NotImplementedError

    def to_parquet(self, dataset: st.Dataset) -> None:
        raise NotImplementedError

    def to_tensorflow(self, dataset: st.Dataset) -> tf.data.Dataset:
        raise NotImplementedError

    def value(self, scalar: st.Scalar) -> st.DataSpecValue:
        raise NotImplementedError

    async def async_value(self, scalar: st.Scalar) -> st.DataSpecValue:
        raise NotImplementedError

    async def async_to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> t.AsyncIterator[pa.RecordBatch]:
        raise NotImplementedError

    async def async_to_pandas(self, dataset: st.Dataset) -> pd.DataFrame:
        raise NotImplementedError

    async def async_to_tensorflow(
        self, dataset: st.Dataset
    ) -> tf.data.Dataset:
        raise NotImplementedError

    def status(self, dataset: st.DataSpec) -> st.Status:
        result = self.storage().last_referring(
            [self, dataset], type_name='Status'
        )
        if result is None:
            raise RuntimeWarning("No status.")
        return t.cast(st.Status, result)

    def sql(
        self,
        dataset: st.Dataset,
        query: str,
        dialect: t.Optional[st.SQLDialect] = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        raise NotImplementedError

    def foreign_keys(self, dataset: st.Dataset) -> t.Dict[st.Path, st.Path]:
        raise NotImplementedError

    def primary_keys(self, dataset: st.Dataset) -> t.List[st.Path]:
        raise NotImplementedError

    def is_big_data(self, dataset: st.Dataset) -> bool:

        status = stt.last_status(dataset)
        if status is not None:
            # check if big_data_present
            big_data_task = status.task(BIG_DATA_TASK)
            # if yes:return answer
            if (big_data_task is not None) and (
                big_data_task.stage() == 'ready'
            ):
                return big_data_task.properties()[IS_BIG_DATA] == str(True)

        if dataset.is_source():
            raise NotImplementedError(
                'Found source dataset without any big data status'
            )
        else:
            parents_list, parents_dict = dataset.parents()
            parents_list.extend(list(parents_dict.values()))
            # parents_list=t.cast(t.Sequence[st.Dataset],parents_list)
            if len(parents_list) > 1:
                raise NotImplementedError(
                    'transforms with many dataspecs not supported yet'
                )
            is_parent_big_data = self.is_big_data(
                parents_list[0]  # type:ignore
            )

            if not is_parent_big_data:
                # write status it is not big data
                stt.ready(
                    dataset,
                    task=BIG_DATA_TASK,
                    properties={
                        IS_BIG_DATA: str(False)
                    },  # we do not need to add more info because a
                    # non big_data dataset cannot become big_data
                )
                return False
            else:
                # check that the transform does not change
                # the big data status
                (
                    is_big_data,
                    number_lines,
                    number_bytes,
                    threshold_kind,
                ) = check_transform_big_data(
                    dataset.transform(), parents_list[0]  # type:ignore
                )
                big_data_threshold = int(
                    stt.last_status(parents_list[0])  # type:ignore
                    .task(BIG_DATA_TASK)
                    .properties()[BIG_DATA_THRESHOLD]
                )
                # write status
                stt.ready(
                    dataset,
                    task=BIG_DATA_TASK,
                    properties={
                        IS_BIG_DATA: str(is_big_data),
                        BIG_DATA_THRESHOLD: str(big_data_threshold),
                        DATASET_N_LINES: str(number_lines),
                        DATASET_N_BYTES: str(number_bytes),
                        THRESHOLD_TYPE: threshold_kind,
                    },
                )
                return is_big_data


def check_transform_big_data(
    transform: st.Transform, parent_dataset: st.Dataset
) -> t.Tuple[bool, int, int, str]:
    """This methods return true if the dataset transformed
    is big_data and False otherwise. This method is called when the parent
    is big_data so if the transform does not
    affect the size, it should return True
    """
    status = stt.last_status(parent_dataset)
    big_data_threshold = int(
        status.task(BIG_DATA_TASK).properties()[  # type:ignore
            BIG_DATA_THRESHOLD
        ]
    )
    threshold_kind = status.task(BIG_DATA_TASK).properties()[  # type:ignore
        THRESHOLD_TYPE
    ]

    parent_n_lines = int(
        status.task(BIG_DATA_TASK).properties()[DATASET_N_LINES]  # type:ignore
    )
    parent_bytes = int(
        status.task(BIG_DATA_TASK).properties()[DATASET_N_BYTES]  # type:ignore
    )

    transform_name = transform.name()
    if transform_name == 'Sample':
        if transform.protobuf().spec.sample.HasField('fraction'):
            fraction = transform.protobuf().spec.sample.fraction
            new_bytes = int(fraction * parent_bytes)
            n_lines = int(fraction * parent_n_lines)

            if threshold_kind == DATASET_N_BYTES:
                return (
                    new_bytes > big_data_threshold,
                    n_lines,
                    new_bytes,
                    threshold_kind,
                )
        else:
            n_lines = transform.protobuf().spec.sample.size
            new_bytes = int(n_lines * parent_bytes / parent_n_lines)

            if threshold_kind == DATASET_N_BYTES:
                big_data_threshold = int(1e5)

        threshold_kind = DATASET_N_LINES

        return n_lines > big_data_threshold, n_lines, new_bytes, threshold_kind

    elif transform_name == 'filter':
        # TODO: we need to save the real sizes of a dataspec in the statuses
        # so that we can check what happens here
        raise NotImplementedError(
            ' Big data status tot implemented yet for filtering'
        )

    elif transform_name == 'Synthetic data':
        # here we should leverage the sampling ratio just to get the size,
        # in any case, synthetic data is never big data
        sampling_ratios = json.loads(transform.properties()['sampling_ratios'])
        synthetic_size = 0
        for table_path, sampling_ratio in zip(
            parent_dataset.schema().tables(), sampling_ratios.values()
        ):
            stat = (
                parent_dataset.size()
                .statistics()
                .nodes_statistics(table_path)[0]
            )
            synthetic_size += int(stat.size() * sampling_ratio)
        threshold_kind = DATASET_N_LINES
        return (
            False,
            synthetic_size,
            int(synthetic_size * parent_bytes / parent_n_lines),
            threshold_kind,
        )

    else:
        # other transforms do not affect size
        if transform_name == 'user_settings':
            warnings.warn(
                'user_settings transform considered to' 'not affect size'
            )
        return True, parent_n_lines, parent_bytes, threshold_kind
