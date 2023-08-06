from functools import wraps
from typing import Any, Callable, Dict, List, cast

import pandas as pd

import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


async def pandas_or_value(dataspec: st.DataSpec) -> Any:
    if dataspec.prototype() == sp.Dataset:
        dataset = cast(st.Dataset, dataspec)
        out = await dataset.async_to_pandas()
        return await select_pandas_data(out, dataset.is_protected())
    else:
        scalar = cast(st.Scalar, dataspec)
        return await scalar.async_value()


async def select_pandas_data(
    dataframe: pd.DataFrame, is_protected: bool
) -> pd.DataFrame:
    if is_protected:
        return pd.DataFrame.from_records(dataframe['data'].values)
    return dataframe


def sarus_external_op(ops_fn: Callable) -> Callable:
    @wraps(ops_fn)
    async def wrapped_ops_fn(
        dataspec: st.DataSpec,
        py_args: Dict[int, Any],
        py_kwargs: Dict[str, Any],
        ds_args_pos: List[int],
    ) -> Any:
        """Collect the referenced Dataspecs, and regorganize the arguments in
        the correct order.

        Args:
            py_args: Serialized Python args, the key is the position in the
            args.
            py_kwargs: Serialized Python kwargs.
            ds_args_pos: The position of Dataspecs args in the args.
        """
        ds_args, ds_kwargs = dataspec.parents()

        ds_values = [await pandas_or_value(ds_arg) for ds_arg in ds_args]
        pos_values = {pos: val for pos, val in zip(ds_args_pos, ds_values)}
        ds_kw_values = {
            name: await pandas_or_value(ds_kwarg)
            for name, ds_kwarg in ds_kwargs.items()
        }

        kwargs = {**py_kwargs, **ds_kw_values}
        pos_args = {**pos_values, **py_args}
        args = [pos_args[i] for i in range(len(pos_args))]

        return await ops_fn(*args, **kwargs)

    return wrapped_ops_fn
