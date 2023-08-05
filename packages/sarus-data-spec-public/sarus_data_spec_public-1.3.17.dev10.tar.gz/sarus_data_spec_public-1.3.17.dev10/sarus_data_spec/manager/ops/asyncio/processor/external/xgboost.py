from __future__ import annotations

from typing import Any

try:
    import xgboost  # type: ignore[import]
except ModuleNotFoundError:
    pass  # error message in typing.py


from .utils import sarus_external_op


@sarus_external_op
async def xgb_fit(
    model: xgboost.XGBClassifier, *args: Any, **kwargs: Any
) -> xgboost.XGBClassifier:
    fitted_model = model.fit(*args, **kwargs)
    return fitted_model


@sarus_external_op
async def xgb_predict(
    model: xgboost.XGBClassifier,
    *args: Any,
    **kwargs: Any,
) -> Any:
    y_pred = model.predict(*args, **kwargs)
    return y_pred


@sarus_external_op
async def xgb_predict_proba(
    model: xgboost.XGBClassifier,
    *args: Any,
    **kwargs: Any,
) -> Any:
    y_pred = model.predict_proba(*args, **kwargs)
    return y_pred
