from typing import Any, List, Tuple, Union
import logging

import pandas as pd

from .utils import sarus_external_op

logger = logging.getLogger(__name__)


@sarus_external_op
async def pd_dataframe(*args: Any, **kwargs: Any) -> Any:
    return pd.DataFrame(*args, **kwargs)


@sarus_external_op
async def pd_series(*args: Any, **kwargs: Any) -> Any:
    return pd.Series(*args, **kwargs)


@sarus_external_op
async def pd_query(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.DataFrame]
    return parent_val.query(*args, **kwargs)


@sarus_external_op
async def pd_ndim(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.ndim


@sarus_external_op
async def pd_name(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.name


@sarus_external_op
async def pd_size(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.size


@sarus_external_op
async def pd_shape(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.shape


@sarus_external_op
async def pd_axes(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.axes


@sarus_external_op
async def pd_columns(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.columns


@sarus_external_op
async def pd_index(parent_val: Any) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.index


@sarus_external_op
async def pd_dtype(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.dtype


@sarus_external_op
async def pd_dtypes(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.dtypes


@sarus_external_op
async def pd_values(parent_val: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.values


@sarus_external_op
async def pd_astype(
    parent_val: Any, *args: Any, **kwargs: Any
) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.astype(*args, **kwargs)


@sarus_external_op
async def pd_reset_index(
    parent_val: Any, *args: Any, **kwargs: Any
) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.reset_index(*args, **kwargs)


@sarus_external_op
async def pd_loc(
    parent_val: Any, key: Tuple[Union[str, slice, List[str]], ...]
) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.loc[key]


@sarus_external_op
async def pd_set_loc(
    parent_val: Any,
    key: Tuple[Union[str, slice, List[str]], ...],
    newvalue: Any,
) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    parent_val.loc[key] = newvalue
    return parent_val


@sarus_external_op
async def pd_iloc(
    parent_val: Any, key: Tuple[Union[str, slice, List[str]], ...]
) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.iloc[key]


@sarus_external_op
async def pd_set_iloc(
    parent_val: Any,
    key: Tuple[Union[str, slice, List[str]], ...],
    newvalue: Any,
) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    parent_val.iloc[key] = newvalue
    return parent_val


@sarus_external_op
async def pd_eq(val_1: Any, val_2: Any) -> pd.DataFrame:
    return val_1 == val_2


@sarus_external_op
async def pd_mean(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.mean(*args, **kwargs)


@sarus_external_op
async def pd_std(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.std(*args, **kwargs)


@sarus_external_op
async def pd_any(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.any(*args, **kwargs)


@sarus_external_op
async def pd_describe(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.describe(*args, **kwargs)


@sarus_external_op
async def pd_head(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.head(*args, **kwargs)


@sarus_external_op
async def pd_mask(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.mask(*args, **kwargs)


@sarus_external_op
async def pd_select_dtypes(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.select_dtypes(*args, **kwargs)


@sarus_external_op
async def pd_quantile(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.quantile(*args, **kwargs)


@sarus_external_op
async def pd_sum(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.sum(*args, **kwargs)


@sarus_external_op
async def pd_add(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.add(*args, **kwargs)


@sarus_external_op
async def pd_sub(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.sub(*args, **kwargs)


@sarus_external_op
async def pd_fillna(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.fillna(*args, **kwargs)


@sarus_external_op
async def pd_round(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.round(*args, **kwargs)


@sarus_external_op
async def pd_reindex(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.reindex(*args, **kwargs)


@sarus_external_op
async def pd_rename(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.rename(*args, **kwargs)


@sarus_external_op
async def pd_count(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.count(*args, **kwargs)


@sarus_external_op
async def pd_transpose(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.transpose(*args, **kwargs)


@sarus_external_op
async def pd_unique(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.unique(*args, **kwargs)


@sarus_external_op
async def pd_value_counts(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.value_counts(*args, **kwargs)


@sarus_external_op
async def pd_to_dict(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.to_dict(*args, **kwargs)


@sarus_external_op
async def pd_apply(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.apply(*args, **kwargs)


@sarus_external_op
async def pd_median(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.median(*args, **kwargs)


@sarus_external_op
async def pd_abs(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.abs(*args, **kwargs)


@sarus_external_op
async def pd_mad(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.mad(*args, **kwargs)


@sarus_external_op
async def pd_skew(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.skew(*args, **kwargs)


@sarus_external_op
async def pd_kurtosis(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.kurtosis(*args, **kwargs)


@sarus_external_op
async def pd_agg(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.agg(*args, **kwargs)


@sarus_external_op
async def pd_droplevel(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.droplevel(*args, **kwargs)


@sarus_external_op
async def pd_replace(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.replace(*args, **kwargs)


@sarus_external_op
async def pd_sort_values(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.sort_values(*args, **kwargs)


@sarus_external_op
async def pd_drop(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.drop(*args, **kwargs)


@sarus_external_op
async def pd_dropna(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.dropna(*args, **kwargs)


@sarus_external_op
async def pd_drop_duplicates(
    parent_val: Any, *args: Any, **kwargs: Any
) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.drop_duplicates(*args, **kwargs)


@sarus_external_op
async def pd_corr(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.corr(*args, **kwargs)


@sarus_external_op
async def pd_get_dummies(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return pd.get_dummies(parent_val, *args, **kwargs)


@sarus_external_op
async def pd_join(val1: Any, *args: Any, **kwargs: Any) -> Any:
    return val1.join(*args, **kwargs)


@sarus_external_op
async def pd_groupby(val1: Any, *args: Any, **kwargs: Any) -> Any:
    return val1.groupby(*args, **kwargs)


@sarus_external_op
async def pd_merge(val1: Any, *args: Any, **kwargs: Any) -> Any:
    return val1.merge(*args, **kwargs)


@sarus_external_op
async def pd_merge_fn(*args: Any, **kwargs: Any) -> Any:
    return pd.merge(*args, **kwargs)


@sarus_external_op
async def pd_concat(*args: Any, **kwargs: Any) -> Any:
    return pd.concat(*args, **kwargs)


@sarus_external_op
async def pd_append(val1: Any, *args: Any, **kwargs: Any) -> Any:
    return val1.append(*args, **kwargs)


@sarus_external_op
async def pd_nunique(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.nunique(*args, **kwargs)


@sarus_external_op
async def pd_isnull(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.isnull(*args, **kwargs)


@sarus_external_op
async def pd_notnull(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.notnull(*args, **kwargs)


@sarus_external_op
async def pd_isin(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.isin(*args, **kwargs)


@sarus_external_op
async def pd_rolling(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    return parent_val.rolling(*args, **kwargs)


@sarus_external_op
async def pd_to_datetime(*args: Any, **kwargs: Any) -> Any:
    return pd.to_datetime(*args, **kwargs)
