# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Voting ensemble"""

import numpy as np
import sklearn
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.ensemble import VotingClassifier
from sklearn.preprocessing import LabelEncoder
from typing import Any, List, Dict, Optional

from .._diagnostics.azureml_error import AzureMLError
from .._diagnostics.error_definitions import GenericFitError, GenericPredictError
from ..score import _scoring_utilities
from .._types import CoreDataInputType


class PreFittedSoftVotingClassifier(VotingClassifier):
    """
    Pre-fitted Soft Voting Classifier class.

    :param estimators: Models to include in the PreFittedSoftVotingClassifier
    :type estimators: list
    :param weights: Weights given to each of the estimators
    :type weights: numpy.ndarray
    :param flatten_transform:
        If True, transform method returns matrix with
        shape (n_samples, n_classifiers * n_classes).
        If False, it returns (n_classifiers, n_samples,
        n_classes).
    :type flatten_transform: bool
    """

    def __init__(
            self, estimators: List[Any], weights: Optional[np.ndarray] = None,
            flatten_transform: Optional[bool] = None,
            classification_labels: Optional[np.ndarray] = None):
        """
        Initialize function for Pre-fitted Soft Voting Classifier class.

        :param estimators:
            Models to include in the PreFittedSoftVotingClassifier
        :type estimators: list
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers * n_classes).
            If False, it returns (n_classifiers, n_samples, n_classes).
        :type flatten_transform: bool
        """
        super().__init__(estimators=estimators,
                         voting='soft',
                         weights=weights,
                         flatten_transform=flatten_transform)
        try:
            self.estimators_ = [est[1] for est in estimators]
            self._labels = classification_labels
            if classification_labels is None:
                self.le_ = LabelEncoder().fit([0])
            else:
                self.le_ = LabelEncoder().fit(classification_labels)
        except Exception as e:
            raise AzureMLError.create(
                GenericFitError, target="PreFittedSoftVotingClassifier", transformer_name=self.__class__.__name__
            ) from e
        # Fill the classes_ property of VotingClassifier which is calculated
        # during fit.
        # This is important for the ONNX convert, when parsing the model object.
        self.classes_ = self.le_.classes_

    def __setstate__(self, state: Dict[str, Any]):
        if "_labels" not in state:
            state["_labels"] = state["le_"].classes_
        super().__setstate__(state)

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        new_params = {
            "estimators": self.estimators,
            "weights": self.weights,
            "flatten_transform": self.flatten_transform,
            "classification_labels": self._labels
        }
        return new_params

    def _collect_probas(self, X: CoreDataInputType) -> np.ndarray:
        """
        Collect predictions from the ensembled models.

        See base implementation and use here:
        https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/ensemble/_voting.py

        This method is overloaded from scikit-learn implementation based on version 0.22.
        This overload is necessary because scikit-learn assumes ensembled models are all
        trained on the same classes. However, AutoML may ensemble models which have been
        trained on different subsets of data (due to subsampling) resulting in different
        train class labels and brings the need to pad predictions.
        """
        probas = [
            _scoring_utilities.pad_predictions(clf.predict_proba(X), clf.classes_, self.classes_)
            for clf in self.estimators_
        ]
        return np.asarray(probas)


if sklearn.__version__ >= '0.21.0':
    from sklearn.ensemble import VotingRegressor

    class PreFittedSoftVotingRegressor(VotingRegressor):
        """
        Pre-fitted Soft Voting Regressor class.

        :param estimators: Models to include in the PreFittedSoftVotingRegressor
        :type estimators: list
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers). If False, it
            returns (n_classifiers, n_samples, 1).
        :type flatten_transform: bool
        """

        def __init__(self, estimators: List[Any], weights: Optional[np.ndarray] = None):
            """
            Initialize function for Pre-fitted Soft Voting Regressor class.

            :param estimators:
                Models to include in the PreFittedSoftVotingRegressor
            :type estimators: list
            :param weights: Weights given to each of the estimators
            :type weights: numpy.ndarray
            :param flatten_transform:
                If True, transform method returns matrix with
                shape (n_samples, n_classifiers). If False, it
                returns (n_classifiers, n_samples, 1).
            :type flatten_transform: bool
            """
            self.estimators_ = [est[1] for est in estimators]
            self._wrappedEnsemble = VotingRegressor(estimators, weights=weights)
            self._wrappedEnsemble.estimators_ = self.estimators_

        def fit(self, X: CoreDataInputType, y: np.ndarray, sample_weight: Optional[np.ndarray] = None):
            """
            Fit function for PreFittedSoftVotingRegressor model.

            :param X: Input data.
            :type X: numpy.ndarray or scipy.sparse.spmatrix
            :param y: Input target values.
            :type y: numpy.ndarray
            :param sample_weight: If None, then samples are equally weighted. This is only supported if all
                underlying estimators support sample weights.
            """
            try:
                return self._wrappedEnsemble.fit(X, y, sample_weight)
            except Exception as e:
                raise AzureMLError.create(
                    GenericFitError, target="PreFittedSoftVotingRegressor", transformer_name=self.__class__.__name__
                ) from e

        def predict(self, X: CoreDataInputType):
            """
            Predict function for Pre-fitted Soft Voting Regressor class.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Weighted average of predicted values.
            """
            try:
                return self._wrappedEnsemble.predict(X)
            except Exception as e:
                raise AzureMLError.create(
                    GenericPredictError, target="PreFittedSoftVotingRegressor",
                    transformer_name=self.__class__.__name__
                ) from e

        def get_params(self, deep: bool = True):
            """
            Return parameters for Pre-fitted Soft Voting Regressor model.

            :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
            :type deep: bool
            :return: dictionary of parameters
            """
            state = {
                "estimators": self._wrappedEnsemble.estimators,
                "weights": self._wrappedEnsemble.weights
            }
            return state

        def set_params(self, **params: Any):
            """
            Set the parameters of this estimator.

            :return: self
            """
            return super(PreFittedSoftVotingRegressor, self).set_params(**params)

        def __setstate__(self, state: Dict[str, Any]):
            """
            Set state for object reconstruction.

            :param state: pickle state
            """
            if '_wrappedEnsemble' in state:
                self._wrappedEnsemble = state['_wrappedEnsemble']
            else:
                # ensure we can load state from previous version of this class
                self._wrappedEnsemble = PreFittedSoftVotingRegressor(state['estimators'], state['weights'])
else:
    class PreFittedSoftVotingRegressor(BaseEstimator, RegressorMixin):  # type: ignore
        """
        Pre-fitted Soft Voting Regressor class.

        :param estimators: Models to include in the PreFittedSoftVotingRegressor
        :type estimators: list
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers). If False, it
            returns (n_classifiers, n_samples, 1).
        :type flatten_transform: bool
        """

        def __init__(self, estimators: List[Any], weights: Optional[np.ndarray] = None,
                     flatten_transform: Optional[bool] = None):
            """
            Initialize function for Pre-fitted Soft Voting Regressor class.

            :param estimators:
                Models to include in the PreFittedSoftVotingRegressor
            :type estimators: list
            :param weights: Weights given to each of the estimators
            :type weights: numpy.ndarray
            :param flatten_transform:
                If True, transform method returns matrix with
                shape (n_samples, n_classifiers). If False, it
                returns (n_classifiers, n_samples, 1).
            :type flatten_transform: bool
            """
            self._wrappedEnsemble = PreFittedSoftVotingClassifier(
                estimators, weights, flatten_transform, classification_labels=[0])

        def fit(self, X: CoreDataInputType, y: np.ndarray, sample_weight: Optional[np.ndarray] = None):
            """
            Fit function for PreFittedSoftVotingRegressor model.

            :param X: Input data.
            :type X: numpy.ndarray or scipy.sparse.spmatrix
            :param y: Input target values.
            :type y: numpy.ndarray
            :param sample_weight: If None, then samples are equally weighted. This is only supported if all
                underlying estimators support sample weights.
            """
            try:
                # We cannot directly call into the wrapped model as the VotingClassifier will label
                # encode y. We get around this problem in the training case by passing in a single
                # classification label [0]. This is also only a problem on scikit-learn<=0.20. On
                # scikit-learn>=0.21, we rely on the VotingRegressor which correctly handles fitting
                # base learners. Imports are intentionally kept within this funciton to ensure compatibility
                # if scikit-learn>0.20 is installed (where this class is unused).

                # This implementation is based on the fit implementation of the VotingClassifier on
                # scikit-learn version 0.20. More information can be found on this branch:
                # https://github.com/scikit-learn/scikit-learn/blob/0.20.X/sklearn/ensemble/voting_classifier.py
                from joblib import Parallel, delayed
                from sklearn.utils import Bunch
                names, clfs = zip(*self._wrappedEnsemble.estimators)

                def _parallel_fit_estimator(estimator: Any, X: CoreDataInputType,
                                            y: np.ndarray, sample_weight: Optional[np.ndarray] = None):
                    """Private function used to fit an estimator within a job."""
                    if sample_weight is not None:
                        estimator.fit(X, y, sample_weight=sample_weight)
                    else:
                        estimator.fit(X, y)
                    return estimator

                self._wrappedEnsemble.estimators_ = Parallel(n_jobs=self._wrappedEnsemble.n_jobs)(
                    delayed(_parallel_fit_estimator)(clone(clf), X, y, sample_weight=sample_weight)
                    for clf in clfs if clf is not None)

                self._wrappedEnsemble.named_estimators_ = Bunch(**dict())
                for k, e in zip(self._wrappedEnsemble.estimators, self._wrappedEnsemble.estimators_):
                    self._wrappedEnsemble.named_estimators_[k[0]] = e
                return self
            except Exception as e:
                raise AzureMLError.create(
                    GenericFitError, target="PreFittedSoftVotingRegressor", transformer_name=self.__class__.__name__
                ) from e

        def predict(self, X: CoreDataInputType):
            """
            Predict function for Pre-fitted Soft Voting Regressor class.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Weighted average of predicted values.
            """
            try:
                predicted = self._wrappedEnsemble._predict(X)
                return np.average(predicted, axis=1, weights=self._wrappedEnsemble.weights)
            except Exception as e:
                raise AzureMLError.create(
                    GenericPredictError, target="PreFittedSoftVotingRegressor",
                    transformer_name=self.__class__.__name__
                ) from e

        def get_params(self, deep: bool = True):
            """
            Return parameters for Pre-fitted Soft Voting Regressor model.

            :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
            :type deep: bool
            :return: dictionary of parameters
            """
            state = {
                "estimators": self._wrappedEnsemble.estimators,
                "weights": self._wrappedEnsemble.weights,
                "flatten_transform": self._wrappedEnsemble.flatten_transform
            }
            return state

        def set_params(self, **params: Any):
            """
            Set the parameters of this estimator.

            :return: self
            """
            return super(PreFittedSoftVotingRegressor, self).set_params(**params)  # type: ignore

        def __setstate__(self, state: Dict[str, Any]):
            """
            Set state for object reconstruction.

            :param state: pickle state
            """
            if '_wrappedEnsemble' in state:
                self._wrappedEnsemble = state['_wrappedEnsemble']
            else:
                # ensure we can load state from previous version of this class
                self._wrappedEnsemble = PreFittedSoftVotingClassifier(
                    state['estimators'], state['weights'], state['flatten_transform'], classification_labels=[0])
