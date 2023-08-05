# -*- coding: utf-8 -*-

from ultron.optimize.model.linearmodel import ConstLinearModel
from ultron.optimize.model.linearmodel import LassoRegression
from ultron.optimize.model.linearmodel import BayesianRegression
from ultron.optimize.model.linearmodel import RidgeRegression
from ultron.optimize.model.linearmodel import TweedieRegression
from ultron.optimize.model.linearmodel import HuberRegression
from ultron.optimize.model.linearmodel import SGDRegression
from ultron.optimize.model.linearmodel import PassiveAggressiveRegression
from ultron.optimize.model.linearmodel import TheilSenRegression
from ultron.optimize.model.linearmodel import LinearRegression
from ultron.optimize.model.linearmodel import LogisticRegression
from ultron.optimize.model.treemodel import RandomForestClassifier
from ultron.optimize.model.treemodel import RandomForestRegressor
from ultron.optimize.model.treemodel import ExtraTreesClassifier
from ultron.optimize.model.treemodel import ExtraTreesRegressor
from ultron.optimize.model.treemodel import BaggingClassifier
from ultron.optimize.model.treemodel import BaggingRegressor
from ultron.optimize.model.treemodel import AdaBoostClassifier
from ultron.optimize.model.treemodel import AdaBoostRegressor
from ultron.optimize.model.treemodel import GradientBoostingClassifier
from ultron.optimize.model.treemodel import GradientBoostingRegressor
from ultron.optimize.model.treemodel import DecisionTreeClassifier
from ultron.optimize.model.treemodel import DecisionTreeRegressor
from ultron.optimize.model.treemodel import XGBClassifier
from ultron.optimize.model.treemodel import XGBRegressor
from ultron.optimize.model.treemodel import XGBTrainer
from ultron.optimize.model.treemodel import LGBMClassifier
from ultron.optimize.model.treemodel import LGBMRegressor
from ultron.optimize.model.treemodel import LGBMTrainer
from ultron.optimize.model.treemodel import VotingRegressor
from ultron.optimize.model.treemodel import VotingClassifier
from ultron.optimize.model.treemodel import StackingClassifier
from ultron.optimize.model.treemodel import StackingRegressor
from ultron.optimize.model.modelbase import ModelBase


def load_model(model_desc):
    model_name = model_desc['model_name']
    model_name_parts = set(model_name.split('.'))

    if 'ConstLinearModel' in model_name_parts:
        return ConstLinearModel.load(model_desc)
    elif 'LinearRegression' in model_name_parts:
        return LinearRegression.load(model_desc)
    elif 'LassoRegression' in model_name_parts:
        return LassoRegression.load(model_desc)
    elif 'BayesianRegression' in model_name_parts:
        return BayesianRegression.load(model_desc)
    elif 'RidgeRegression' in model_name_parts:
        return RidgeRegression.load(model_desc)
    elif 'TweedieRegression' in model_name_parts:
        return TweedieRegression.load(model_desc)
    elif 'HuberRegression' in model_name_parts:
        return HuberRegression.load(model_desc)
    elif 'SGDRegression' in model_name_parts:
        return SGDRegression.load(model_desc)
    elif 'PassiveAggressiveRegression' in model_name_parts:
        return PassiveAggressiveRegression.load(model_desc)
    elif 'TheilSenRegression' in model_name_parts:
        return TheilSenRegression.load(model_desc)
    elif 'LogisticRegression' in model_name_parts:
        return LogisticRegression.load(model_desc)
    elif 'RandomForestRegressor' in model_name_parts:
        return RandomForestRegressor.load(model_desc)
    elif 'RandomForestClassifier' in model_name_parts:
        return RandomForestClassifier.load(model_desc)
    elif 'ExtraTreesClassifier' in model_name_parts:
        return ExtraTreesClassifier.load(model_desc)
    elif 'ExtraTreesRegressor' in model_name_parts:
        return ExtraTreesRegressor.load(model_desc)
    elif 'BaggingClassifier' in model_name_parts:
        return BaggingClassifier.load(model_desc)
    elif 'BaggingRegressor' in model_name_parts:
        return BaggingRegressor.load(model_desc)
    elif 'AdaBoostClassifier' in model_name_parts:
        return AdaBoostClassifier.load(model_desc)
    elif 'AdaBoostRegressor' in model_name_parts:
        return AdaBoostRegressor.load(model_desc)
    elif 'GradientBoostingRegressor' in model_name_parts:
        return GradientBoostingRegressor.load(model_desc)
    elif 'GradientBoostingClassifier' in model_name_parts:
        return GradientBoostingClassifier.load(model_desc)
    elif 'DecisionTreeClassifier' in model_name_parts:
        return DecisionTreeClassifier.load(model_desc)
    elif 'DecisionTreeRegressor' in model_name_parts:
        return DecisionTreeRegressor.load(model_desc)
    elif 'XGBRegressor' in model_name_parts:
        return XGBRegressor.load(model_desc)
    elif 'XGBClassifier' in model_name_parts:
        return XGBClassifier.load(model_desc)
    elif 'XGBTrainer' in model_name_parts:
        return XGBTrainer.load(model_desc)
    elif 'LGBMRegressor' in model_name_parts:
        return LGBMRegressor.load(model_desc)
    elif 'LGBMClassifier' in model_name_parts:
        return LGBMClassifier.load(model_desc)
    elif 'LGBMTrainer' in model_name_parts:
        return LGBMTrainer.load(model_desc)
    elif 'VotingRegressor' in model_name_parts:
        return VotingRegressor.load(model_desc)
    elif 'VotingClassifier' in model_name_parts:
        return VotingClassifier.load(model_desc)
    elif 'StackingClassifier' in model_name_parts:
        return StackingClassifier.load(model_desc)
    elif 'StackingRegressor' in model_name_parts:
        return StackingRegressor.load(model_desc)
    else:
        raise ValueError(
            '{0} is not currently supported in model loader.'.format(
                model_name))
