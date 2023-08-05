# -*- coding: utf-8 -*-

from lib2to3.pgen2.literals import evalString
from tabnanny import verbose
import arrow, pdb
import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb

from sklearn.ensemble import RandomForestClassifier as RandomForestClassifierImpl
from sklearn.ensemble import RandomForestRegressor as RandomForestRegressorImpl
from sklearn.ensemble import ExtraTreesClassifier as ExtraTreesClassifierImpl
from sklearn.ensemble import ExtraTreesRegressor as ExtraTreesRegressorImpl
from sklearn.ensemble import BaggingClassifier as BaggingClassifierImpl
from sklearn.ensemble import BaggingRegressor as BaggingRegressorImpl
from sklearn.ensemble import AdaBoostClassifier as AdaBoostClassifierImpl
from sklearn.ensemble import AdaBoostRegressor as AdaBoostRegressorImpl
from sklearn.ensemble import VotingClassifier as VotingClassifierImpl
from sklearn.ensemble import VotingRegressor as VotingRegressorImpl
from sklearn.ensemble import GradientBoostingClassifier as GradientBoostingClassifierImpl
from sklearn.ensemble import GradientBoostingRegressor as GradientBoostingRegressorImpl
from mlxtend.classifier import StackingClassifier as StackingClassifierImpl
from mlxtend.regressor import StackingRegressor as StackingRegressorImpl
from sklearn.tree import DecisionTreeClassifier as DecisionTreeClassifierImpl
from sklearn.tree import DecisionTreeRegressor as DecisionTreeRegressorImpl
from xgboost import XGBClassifier as XGBClassifierImpl
from xgboost import XGBRegressor as XGBRegressorImpl
from lightgbm import LGBMClassifier as LGBMClassifierImpl
from lightgbm import LGBMRegressor as LGBMRegressorImpl
from sklearn.model_selection import train_test_split

from ultron.optimize.model.modelbase import create_model_base


class RandomForestRegressor(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 max_features: str = 'auto',
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = RandomForestRegressorImpl(n_estimators=n_estimators,
                                              max_features=max_features,
                                              **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class RandomForestClassifier(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 max_features: str = 'auto',
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = RandomForestClassifierImpl(n_estimators=n_estimators,
                                               max_features=max_features,
                                               **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class ExtraTreesClassifier(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 max_features: str = 'auto',
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = ExtraTreesClassifierImpl(n_estimators=n_estimators,
                                             max_features=max_features,
                                             **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class ExtraTreesRegressor(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 max_features: str = 'auto',
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = ExtraTreesRegressorImpl(n_estimators=n_estimators,
                                            max_features=max_features,
                                            **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class BaggingClassifier(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 max_features: float = 1.0,
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = BaggingClassifierImpl(n_estimators=n_estimators,
                                          max_features=max_features,
                                          **kwargs)

    @property
    def importances(self):
        return self.impl.estimators_features_


class BaggingRegressor(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 max_features: float = 1.0,
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = BaggingRegressorImpl(n_estimators=n_estimators,
                                         max_features=max_features,
                                         **kwargs)

    @property
    def importances(self):
        return self.impl.estimators_features_


class AdaBoostClassifier(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 learning_rate: float = 1.0,
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = AdaBoostClassifierImpl(n_estimators=n_estimators,
                                           learning_rate=learning_rate,
                                           **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class AdaBoostRegressor(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 learning_rate: float = 1.0,
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = AdaBoostRegressorImpl(n_estimators=n_estimators,
                                          learning_rate=learning_rate,
                                          **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class GradientBoostingClassifier(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 max_features: float = 1.0,
                 learning_rate: float = 0.1,
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = GradientBoostingClassifierImpl(n_estimators=n_estimators,
                                                   max_features=max_features,
                                                   learning_rate=learning_rate,
                                                   **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class GradientBoostingRegressor(create_model_base('sklearn')):

    def __init__(self,
                 n_estimators: int = 100,
                 max_features: float = 1.0,
                 learning_rate: float = 0.1,
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = GradientBoostingRegressorImpl(n_estimators=n_estimators,
                                                  max_features=max_features,
                                                  learning_rate=learning_rate,
                                                  **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class DecisionTreeClassifier(create_model_base('sklearn')):

    def __init__(self, features=None, fit_target=None, **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = DecisionTreeClassifierImpl(**kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class DecisionTreeRegressor(create_model_base('sklearn')):

    def __init__(self, features=None, fit_target=None, **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = DecisionTreeRegressorImpl(**kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class VotingRegressor(create_model_base('sklearn')):

    def __init__(self,
                 estimators=[],
                 voting='hard',
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = VotingRegressorImpl(estimators=estimators,
                                        voting=voting,
                                        **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class VotingClassifier(create_model_base('sklearn')):

    def __init__(self,
                 estimators=[],
                 voting='hard',
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = VotingClassifierImpl(estimators=estimators,
                                         voting=voting,
                                         **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class StackingClassifier(create_model_base('mlxtend')):

    def __init__(self,
                 classifiers=[],
                 meta_classifier=None,
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = StackingClassifierImpl(classifiers=classifiers,
                                           meta_classifier=meta_classifier,
                                           **kwargs)

    @property
    def importances(self):
        return self.impl.clfs_


class StackingRegressor(create_model_base('mlxtend')):

    def __init__(self,
                 regressors=[],
                 meta_regressor=None,
                 features=None,
                 fit_target=None,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = StackingRegressorImpl(regressors=regressors,
                                          meta_regressor=meta_regressor,
                                          **kwargs)

    @property
    def importances(self):
        return self.impl.clfs_


class LGBMRegressor(create_model_base('lightgbm')):

    def __init__(self,
                 n_estimators: int = 100,
                 learning_rate: float = 0.1,
                 max_depth: int = 3,
                 features=None,
                 fit_target=None,
                 n_jobs: int = 1,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = LGBMRegressorImpl(n_estimators=n_estimators,
                                      max_depth=max_depth,
                                      learning_rate=learning_rate,
                                      n_jobs=n_jobs,
                                      **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class LGBMClassifier(create_model_base('lightgbm')):

    def __init__(self,
                 n_estimators: int = 100,
                 learning_rate: float = 0.1,
                 max_depth: int = 3,
                 features=None,
                 fit_target=None,
                 n_jobs: int = 1,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = LGBMClassifierImpl(n_estimators=n_estimators,
                                       max_depth=max_depth,
                                       learning_rate=learning_rate,
                                       n_jobs=n_jobs,
                                       **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class LGBMTrainer(create_model_base('lightgbm')):

    def __init__(self,
                 objective='multiclass',
                 n_estimators: int = 100,
                 learning_rate: float = 0.1,
                 max_depth: int = 3,
                 num_class: int = 2,
                 feature_fraction=0.9,
                 bagging_fraction=0.95,
                 eval_sample=None,
                 early_stopping_rounds=None,
                 features=None,
                 fit_target=None,
                 n_jobs: int = 1,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.params = {
            'objective': objective,
            'learning_rate': learning_rate,
            'max_depth': max_depth,
            'metric': ['multi_error', 'multi_logloss'],
            'feature_fraction': feature_fraction,
            'bagging_fraction': bagging_fraction,
            'n_jobs': n_jobs
        }
        self.eval_sample = eval_sample
        self.num_boost_round = n_estimators
        self.early_stopping_rounds = early_stopping_rounds
        self.impl = None
        self.kwargs = kwargs
        self.trained_time = None

    def fit(self, x: pd.DataFrame, y: np.ndarray):
        if self.eval_sample:
            x_train, x_eval, y_train, y_eval = train_test_split(
                x[self.features].values,
                y,
                test_size=self.eval_sample,
                random_state=42)
            d_train = lgb.Dataset(x_train, y_train)
            d_eval = lgb.Dataset(x_eval, y_eval)
            self.impl = lgb.train(self.params,
                                  d_train,
                                  num_boost_round=self.num_boost_round,
                                  evals=[(d_eval, 'eval')],
                                  verbose_eval=False,
                                  **self.kwargs)
        else:
            d_train = lgb.Dataset(x[self.features].values, y)
            self.impl = lgb.train(self.params,
                                  d_train,
                                  num_boost_round=self.num_boost_round,
                                  **self.kwargs)
            self.trained_time = arrow.now().format("YYYY-MM-DD HH:mm:ss")

    def predict(self, x: pd.DataFrame) -> np.ndarray:
        return self.impl.predict(x[self.features].values)

    @property
    def importances(self):
        imps = self.impl.get_fscore().items()
        imps = sorted(imps, key=lambda x: x[0])
        return list(zip(*imps))[1]


class XGBRegressor(create_model_base('xgboost')):

    def __init__(self,
                 n_estimators: int = 100,
                 learning_rate: float = 0.1,
                 max_depth: int = 3,
                 features=None,
                 fit_target=None,
                 n_jobs: int = 1,
                 missing: float = np.nan,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = XGBRegressorImpl(n_estimators=n_estimators,
                                     learning_rate=learning_rate,
                                     max_depth=max_depth,
                                     n_jobs=n_jobs,
                                     missing=missing,
                                     **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class XGBClassifier(create_model_base('xgboost')):

    def __init__(self,
                 n_estimators: int = 100,
                 learning_rate: float = 0.1,
                 max_depth: int = 3,
                 features=None,
                 fit_target=None,
                 n_jobs: int = 1,
                 missing: float = np.nan,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = XGBClassifierImpl(n_estimators=n_estimators,
                                      learning_rate=learning_rate,
                                      max_depth=max_depth,
                                      n_jobs=n_jobs,
                                      missing=missing,
                                      **kwargs)

    @property
    def importances(self):
        return self.impl.feature_importances_.tolist()


class XGBTrainer(create_model_base('xgboost')):

    def __init__(self,
                 objective='binary:logistic',
                 booster='gbtree',
                 tree_method='hist',
                 n_estimators: int = 100,
                 learning_rate: float = 0.1,
                 max_depth=3,
                 eval_sample=None,
                 early_stopping_rounds=None,
                 subsample=1.,
                 colsample_bytree=1.,
                 features=None,
                 fit_target=None,
                 random_state: int = 0,
                 n_jobs: int = 1,
                 **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.params = {
            'objective': objective,
            'max_depth': max_depth,
            'eta': learning_rate,
            'booster': booster,
            'tree_method': tree_method,
            'subsample': subsample,
            'colsample_bytree': colsample_bytree,
            'nthread': n_jobs,
            'seed': random_state
        }
        self.eval_sample = eval_sample
        self.num_boost_round = n_estimators
        self.early_stopping_rounds = early_stopping_rounds
        self.impl = None
        self.kwargs = kwargs
        self.trained_time = None

    def fit(self, x: pd.DataFrame, y: np.ndarray):
        if self.eval_sample:
            x_train, x_eval, y_train, y_eval = train_test_split(
                x[self.features].values,
                y,
                test_size=self.eval_sample,
                random_state=42)
            d_train = xgb.DMatrix(x_train, y_train)
            d_eval = xgb.DMatrix(x_eval, y_eval)
            self.impl = xgb.train(params=self.params,
                                  dtrain=d_train,
                                  num_boost_round=self.num_boost_round,
                                  evals=[(d_eval, 'eval')],
                                  verbose_eval=False,
                                  **self.kwargs)
        else:
            d_train = xgb.DMatrix(x[self.features].values, y)
            self.impl = xgb.train(params=self.params,
                                  dtrain=d_train,
                                  num_boost_round=self.num_boost_round,
                                  **self.kwargs)

        self.trained_time = arrow.now().format("YYYY-MM-DD HH:mm:ss")

    def predict(self, x: pd.DataFrame) -> np.ndarray:
        d_predict = xgb.DMatrix(x[self.features].values)
        return self.impl.predict(d_predict)

    @property
    def importances(self):
        imps = self.impl.get_fscore().items()
        imps = sorted(imps, key=lambda x: x[0])
        return list(zip(*imps))[1]