# -*- coding: utf-8 -*-
import pdb
import numpy as np
from sklearn.linear_model import LinearRegression as LinearRegressionImpl
from sklearn.linear_model import Lasso as LassoRegressionImpl
from sklearn.linear_model import LogisticRegression as LogisticRegressionImpl
from sklearn.linear_model import BayesianRidge as BayesianRidgeImpl
from sklearn.linear_model import Ridge as RidgeImpl
from sklearn.linear_model import TweedieRegressor as TweedieRegressorImpl
from sklearn.linear_model import HuberRegressor as HuberRegressorImpl
from sklearn.linear_model import SGDRegressor as SGDRegressorImpl
from sklearn.linear_model import PassiveAggressiveRegressor as PassiveAggressiveRegressorImpl
from sklearn.linear_model import TheilSenRegressor as TheilSenRegressorImpl
from ultron.optimize.model.modelbase import create_model_base


class ConstLinearModelImpl(object):

    def __init__(self, weights: np.ndarray = None):
        self.weights = weights.flatten()

    def fit(self, x: np.ndarray, y: np.ndarray):
        raise NotImplementedError(
            "Const linear model doesn't offer fit methodology")

    def predict(self, x: np.ndarray):
        return x @ self.weights

    def score(self, x: np.ndarray, y: np.ndarray) -> float:
        y_hat = self.predict(x)
        y_bar = y.mean()
        ssto = ((y - y_bar)**2).sum()
        sse = ((y - y_hat)**2).sum()
        return 1. - sse / ssto


class ConstLinearModel(create_model_base()):

    def __init__(self, features=None, weights: dict = None, fit_target=None):
        super().__init__(features=features, fit_target=fit_target)
        if features is not None and weights is not None:
            assert (len(features) == len(weights), ValueError,
                    "length of features is not equal to length of weights")
        if weights:
            self.impl = ConstLinearModelImpl(
                np.array([weights[name] for name in self.features]))

    def save(self):
        model_desc = super().save()
        model_desc['weight'] = list(self.impl.weights)
        return model_desc

    @classmethod
    def load(cls, model_desc: dict):
        return super().load(model_desc)

    @property
    def weights(self):
        return self.impl.weights.tolist()


class LinearRegression(create_model_base('sklearn')):

    def __init__(self,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = LinearRegressionImpl(fit_intercept=fit_intercept, **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class LassoRegression(create_model_base('sklearn')):

    def __init__(self,
                 alpha=0.01,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = LassoRegressionImpl(alpha=alpha,
                                        fit_intercept=fit_intercept,
                                        **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class BayesianRegression(create_model_base('sklearn')):

    def __init__(self,
                 alpha=0.01,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = BayesianRidgeImpl(alpha_1=alpha,
                                      fit_intercept=fit_intercept,
                                      **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class RidgeRegression(create_model_base('sklearn')):

    def __init__(self,
                 alpha=0.01,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = RidgeImpl(alpha=alpha,
                              fit_intercept=fit_intercept,
                              **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class TweedieRegression(create_model_base('sklearn')):

    def __init__(self,
                 alpha=0.01,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = TweedieRegressorImpl(alpha=alpha,
                                         fit_intercept=fit_intercept,
                                         **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class HuberRegression(create_model_base('sklearn')):

    def __init__(self,
                 alpha=0.01,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = HuberRegressorImpl(alpha=alpha,
                                       fit_intercept=fit_intercept,
                                       **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class SGDRegression(create_model_base('sklearn')):

    def __init__(self,
                 alpha=0.001,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = SGDRegressorImpl(alpha=alpha,
                                     fit_intercept=fit_intercept,
                                     **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class PassiveAggressiveRegression(create_model_base('sklearn')):

    def __init__(self,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = PassiveAggressiveRegressorImpl(fit_intercept=fit_intercept,
                                                   **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class TheilSenRegression(create_model_base('sklearn')):

    def __init__(self,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = TheilSenRegressorImpl(fit_intercept=fit_intercept,
                                          **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()


class LogisticRegression(create_model_base('sklearn')):

    def __init__(self,
                 features=None,
                 fit_intercept: bool = False,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = LogisticRegressionImpl(fit_intercept=fit_intercept,
                                           **kwargs)

    def save(self) -> dict:
        model_desc = super().save()
        model_desc['weight'] = self.impl.coef_.tolist()
        return model_desc

    @property
    def weights(self):
        return self.impl.coef_.tolist()
