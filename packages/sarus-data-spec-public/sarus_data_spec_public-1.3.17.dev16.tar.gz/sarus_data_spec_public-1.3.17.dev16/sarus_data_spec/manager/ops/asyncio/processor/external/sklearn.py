from __future__ import annotations

from typing import Any

try:
    from sklearn import (
        compose,
        inspection,
        metrics,
        model_selection,
        pipeline,
        preprocessing,
    )
except ModuleNotFoundError:
    pass  # error message in typing.py

from .utils import sarus_external_op


@sarus_external_op
async def model_fit(model: Any, *args: Any, **kwargs: Any) -> Any:
    fitted_model = model.fit(*args, **kwargs)
    return fitted_model


@sarus_external_op
async def sk_get_n_splits(model: Any, *args: Any, **kwargs: Any) -> Any:
    return model.split(*args, **kwargs)


@sarus_external_op
async def sk_inverse_transform(model: Any, *args: Any, **kwargs: Any) -> Any:
    return model.inverse_transform(*args, **kwargs)


@sarus_external_op
async def sk_predict(model: Any, *args: Any, **kwargs: Any) -> Any:
    return model.predict(*args, **kwargs)


@sarus_external_op
async def sk_predict_log_proba(model: Any, *args: Any, **kwargs: Any) -> Any:
    return model.predict_log_proba(*args, **kwargs)


@sarus_external_op
async def sk_predict_proba(model: Any, *args: Any, **kwargs: Any) -> Any:
    return model.predict_proba(*args, **kwargs)


@sarus_external_op
async def sk_split(model: Any, *args: Any, **kwargs: Any) -> Any:
    return model.split(*args, **kwargs)


@sarus_external_op
async def sk_score(model: Any, *args: Any, **kwargs: Any) -> Any:
    return model.score(*args, **kwargs)


@sarus_external_op
async def sk_transform(model: Any, *args: Any, **kwargs: Any) -> Any:
    return model.transform(*args, **kwargs)


@sarus_external_op
async def sk_scale(val: Any, *args: Any, **kwargs: Any) -> Any:
    return preprocessing.scale(val, *args, **kwargs)


@sarus_external_op
async def sk_cross_val_score(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return model_selection.cross_val_score(*args, **kwargs)


@sarus_external_op
async def sk_train_test_split(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return model_selection.train_test_split(*args, **kwargs)


# metrics
@sarus_external_op
async def sk_accuracy_score(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.accuracy_score(*args, **kwargs)


@sarus_external_op
async def sk_average_precision_score(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.average_precision_score(*args, **kwargs)


@sarus_external_op
async def sk_classification_report(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.classification_report(*args, **kwargs)


@sarus_external_op
async def sk_confusion_matrix(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.confusion_matrix(*args, **kwargs)


@sarus_external_op
async def sk_f1_score(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.f1_score(*args, **kwargs)


@sarus_external_op
async def sk_plot_confusion_matrix(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.plot_confusion_matrix(*args, **kwargs)


@sarus_external_op
async def sk_precision_recall_curve(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.precision_recall_curve(*args, **kwargs)


@sarus_external_op
async def sk_precision_score(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.precision_score(*args, **kwargs)


@sarus_external_op
async def sk_recall_score(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.recall_score(*args, **kwargs)


@sarus_external_op
async def sk_roc_auc_score(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.roc_auc_score(*args, **kwargs)


@sarus_external_op
async def sk_auc(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.auc(*args, **kwargs)


@sarus_external_op
async def sk_roc_curve(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.roc_curve(*args, **kwargs)


@sarus_external_op
async def sk_plot_roc_curve(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.plot_roc_curve(*args, **kwargs)


@sarus_external_op
async def sk_plot_precision_recall_curve(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return metrics.plot_precision_recall_curve(*args, **kwargs)


@sarus_external_op
async def sk_label_encoder_fit_transform(
    model: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    X_transformed = model.fit_transform(*args, **kwargs)
    return X_transformed


@sarus_external_op
async def sk_permutation_importance(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return inspection.permutation_importance(*args, **kwargs)


@sarus_external_op
async def sk_pipeline(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return pipeline.Pipeline(*args, **kwargs)


@sarus_external_op
async def sk_function_transformer(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return preprocessing.FunctionTransformer(*args, **kwargs)


@sarus_external_op
async def sk_column_transformer(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return compose.ColumnTransformer(*args, **kwargs)


@sarus_external_op
async def sk_time_series_split(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return model_selection.TimeSeriesSplit(*args, **kwargs)
