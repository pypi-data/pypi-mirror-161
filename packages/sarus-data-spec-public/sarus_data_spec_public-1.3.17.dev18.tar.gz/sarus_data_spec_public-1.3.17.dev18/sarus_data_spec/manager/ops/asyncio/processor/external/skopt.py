from __future__ import annotations

from typing import Any

try:
    import skopt
except ModuleNotFoundError:
    pass  # error message in typing.py

from .utils import sarus_external_op


@sarus_external_op
async def skopt_bayes_search_cv(*args: Any, **kwargs: Any) -> Any:
    return skopt.BayesSearchCV(*args, **kwargs)
