from typing import Any

import numpy as np

from .utils import sarus_external_op


@sarus_external_op
async def np_array(*args: Any, **kwargs: Any) -> Any:
    return np.array(*args, **kwargs)


@sarus_external_op
async def np_astype(val: Any, *args: Any, **kwargs: Any) -> Any:
    return val.astype(*args, **kwargs)


@sarus_external_op
async def np_mean(*args: Any, **kwargs: Any) -> Any:
    return np.mean(*args, **kwargs)


@sarus_external_op
async def np_rand(*args: int) -> Any:
    return np.random.rand(*args)


@sarus_external_op
async def np_std(*args: Any, **kwargs: Any) -> Any:
    return np.std(*args, **kwargs)
