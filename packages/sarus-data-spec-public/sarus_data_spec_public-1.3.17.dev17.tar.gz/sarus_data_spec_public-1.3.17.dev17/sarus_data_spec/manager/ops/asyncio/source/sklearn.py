from __future__ import annotations

from typing import Any, Dict
import pickle as pkl

try:
    from sklearn import (
        cluster,
        decomposition,
        ensemble,
        model_selection,
        preprocessing,
        svm,
    )
    import xgboost  # type: ignore[import]
except ModuleNotFoundError:
    pass  # error message in typing.py

import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


async def create_model(scalar: st.Scalar) -> Any:
    model_spec = scalar.protobuf().spec.model

    args = pkl.loads(model_spec.arguments)
    kwargs = pkl.loads(model_spec.named_arguments)

    model_mapping: Dict["sp.Scalar.Model.ModelClass.V", Any] = {
        sp.Scalar.Model.ModelClass.SK_SVC: svm.SVC,
        sp.Scalar.Model.ModelClass.SK_PCA: decomposition.PCA,
        # preprocessing
        sp.Scalar.Model.ModelClass.SK_ONEHOT: preprocessing.OneHotEncoder,
        sp.Scalar.Model.ModelClass.SK_LABEL_ENCODER: preprocessing.LabelEncoder,
        # cluster
        sp.Scalar.Model.ModelClass.SK_AFFINITY_PROPAGATION: cluster.AffinityPropagation,
        sp.Scalar.Model.ModelClass.SK_AGGLOMERATIVE_CLUSTERING: cluster.AgglomerativeClustering,
        sp.Scalar.Model.ModelClass.SK_BIRCH: cluster.Birch,
        sp.Scalar.Model.ModelClass.SK_DBSCAN: cluster.DBSCAN,
        sp.Scalar.Model.ModelClass.SK_FEATURE_AGGLOMERATION: cluster.FeatureAgglomeration,
        sp.Scalar.Model.ModelClass.SK_KMEANS: cluster.KMeans,
        sp.Scalar.Model.ModelClass.SK_MINIBATCH_KMEANS: cluster.MiniBatchKMeans,
        sp.Scalar.Model.ModelClass.SK_MEAN_SHIFT: cluster.MeanShift,
        sp.Scalar.Model.ModelClass.SK_OPTICS: cluster.OPTICS,
        sp.Scalar.Model.ModelClass.SK_SPECTRAL_CLUSTERING: cluster.SpectralClustering,
        sp.Scalar.Model.ModelClass.SK_SPECTRAL_BICLUSTERING: cluster.SpectralBiclustering,
        sp.Scalar.Model.ModelClass.SK_SPECTRAL_COCLUSTERING: cluster.SpectralCoclustering,
        # ensemble
        sp.Scalar.Model.ModelClass.SK_ADABOOST_CLASSIFIER: ensemble.AdaBoostClassifier,
        sp.Scalar.Model.ModelClass.SK_ADABOOST_REGRESSOR: ensemble.AdaBoostRegressor,
        sp.Scalar.Model.ModelClass.SK_BAGGING_CLASSIFIER: ensemble.BaggingClassifier,
        sp.Scalar.Model.ModelClass.SK_BAGGING_REGRESSOR: ensemble.BaggingRegressor,
        sp.Scalar.Model.ModelClass.SK_EXTRA_TREES_CLASSIFIER: ensemble.ExtraTreesClassifier,
        sp.Scalar.Model.ModelClass.SK_EXTRA_TREES_REGRESSOR: ensemble.ExtraTreesRegressor,
        sp.Scalar.Model.ModelClass.SK_GRADIENT_BOOSTING_CLASSIFIER: ensemble.GradientBoostingClassifier,
        sp.Scalar.Model.ModelClass.SK_GRADIENT_BOOSTING_REGRESSOR: ensemble.GradientBoostingRegressor,
        sp.Scalar.Model.ModelClass.SK_ISOLATION_FOREST: ensemble.IsolationForest,
        sp.Scalar.Model.ModelClass.SK_RANDOM_FOREST_CLASSIFIER: ensemble.RandomForestClassifier,
        sp.Scalar.Model.ModelClass.SK_RANDOM_FOREST_REGRESSOR: ensemble.RandomForestRegressor,
        sp.Scalar.Model.ModelClass.SK_RANDOM_TREES_EMBEDDING: ensemble.RandomTreesEmbedding,
        sp.Scalar.Model.ModelClass.SK_STACKING_CLASSIFIER: ensemble.StackingClassifier,
        sp.Scalar.Model.ModelClass.SK_STACKING_REGRESSOR: ensemble.StackingRegressor,
        sp.Scalar.Model.ModelClass.SK_VOTING_CLASSIFIER: ensemble.VotingClassifier,
        sp.Scalar.Model.ModelClass.SK_VOTING_REGRESSOR: ensemble.VotingRegressor,
        sp.Scalar.Model.ModelClass.SK_HIST_GRADIENT_BOOSTING_CLASSIFIER: ensemble.HistGradientBoostingClassifier,
        sp.Scalar.Model.ModelClass.SK_HIST_GRADIENT_BOOSTING_REGRESSOR: ensemble.HistGradientBoostingRegressor,
        # model_selection
        sp.Scalar.Model.ModelClass.SK_REPEATED_STRATIFIED_KFOLD: model_selection.RepeatedStratifiedKFold,
        sp.Scalar.Model.ModelClass.SK_KFOLD: model_selection.KFold,
        # xgb
        sp.Scalar.Model.ModelClass.XGB_CLASSIFIER: xgboost.XGBClassifier,
    }
    ModelClass = model_mapping[model_spec.model_class]

    return ModelClass(*args, **kwargs)
