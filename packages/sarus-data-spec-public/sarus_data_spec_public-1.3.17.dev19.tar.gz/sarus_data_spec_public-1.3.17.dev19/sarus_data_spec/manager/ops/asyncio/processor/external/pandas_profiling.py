from typing import Any

try:
    from pandas_profiling import ProfileReport
except ModuleNotFoundError:
    pass  # error message in typing.py

from .utils import sarus_external_op


@sarus_external_op
async def pd_profile_report(df: Any, *args: Any, **kwargs: Any) -> Any:
    return ProfileReport(df, *args, **kwargs)
