# -*- coding: utf-8 -*-
from pyexpat import model
import unittest

import numpy as np
import pandas as pd
import pdb
from sklearn.linear_model import LinearRegression as LinearRegression2
from sklearn.linear_model import Lasso as Lasso2
from sklearn.linear_model import LogisticRegression as LogisticRegression2
from sklearn.linear_model import BayesianRidge as BayesianRidge2
from sklearn.linear_model import Ridge as Ridge2
from sklearn.linear_model import TweedieRegressor as TweedieRegressor2
from sklearn.linear_model import HuberRegressor as HuberRegressor2
from sklearn.linear_model import SGDRegressor as SGDRegressor2
from sklearn.linear_model import PassiveAggressiveRegressor as PassiveAggressiveRegressor2
from sklearn.linear_model import TheilSenRegressor as TheilSenRegressor2

from ultron.optimize.model.linearmodel import ConstLinearModel
from ultron.optimize.model.linearmodel import LinearRegression
from ultron.optimize.model.linearmodel import LassoRegression
from ultron.optimize.model.linearmodel import LogisticRegression
from ultron.optimize.model.linearmodel import BayesianRegression
from ultron.optimize.model.linearmodel import RidgeRegression
from ultron.optimize.model.linearmodel import HuberRegression
from ultron.optimize.model.linearmodel import SGDRegression
from ultron.optimize.model.linearmodel import TweedieRegression
from ultron.optimize.model.linearmodel import PassiveAggressiveRegression
from ultron.optimize.model.linearmodel import TheilSenRegression
from ultron.optimize.model.loader import load_model

class LinearModel(unittest.TestCase):
    def setUp(self):
        self.n = 3
        self.features = ['a', 'b', 'c']
        self.train_x = pd.DataFrame(np.random.randn(1000, self.n), columns=self.features)
        self.train_y = np.random.randn(1000)
        self.train_y_label = np.where(self.train_y > 0., 1, 0)
        self.predict_x = pd.DataFrame(np.random.randn(10, self.n), columns=self.features)
    
    def test_const_linear_model(self):
        features = ['c','b','a']
        weights = dict(c=3., b=2., a=1.)
        model = ConstLinearModel(features=features,
                            weights=weights)
        calculated_y = model.predict(self.predict_x)
        expected_y = self.predict_x[features] @ np.array([weights[f] for f in features])
        np.testing.assert_array_almost_equal(calculated_y, expected_y)
    
    def test_const_linear_model_persistence(self):
        weights = dict(c=3., b=2., a=1.)
        model = ConstLinearModel(features=['a','b','c'],
                                    weights=weights)
        
        desc = model.save()
        new_model = load_model(desc)

        self.assertEqual(model.features, new_model.features)
        np.testing.assert_array_almost_equal(model.weights, new_model.weights)
    
    def test_const_linear_model_score(self):
        model = LinearRegression(['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        expected_score = model.score(self.train_x, self.train_y)

        const_model = ConstLinearModel(features=['a', 'b', 'c'],
                                       weights=dict(zip(model.features, model.weights)))

        calculated_score = const_model.score(self.train_x, self.train_y)

        self.assertAlmostEqual(expected_score, calculated_score)

    def test_linear_regression_persistence(self):
        model = LinearRegression(['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)
    
    def test_logistic_regression(self):
        model = LogisticRegression(['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y_label)

        calculated_y = model.predict(self.predict_x)

        expected_model = LogisticRegression2(fit_intercept=False)
        expected_model.fit(self.train_x, self.train_y_label)
        expected_y = expected_model.predict(self.predict_x)


        np.testing.assert_array_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(expected_model.coef_, model.weights)

    def test_logistic_regression_persistence(self):
        model = LogisticRegression(['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y_label)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)

    def test_bayesian_regression(self):
        model = BayesianRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        calculated_y = model.predict(self.predict_x)

        expected_model = BayesianRidge2(alpha_1=0.01, fit_intercept=False)
        expected_model.fit(self.train_x, self.train_y)
        expected_y = expected_model.predict(self.predict_x)

        np.testing.assert_array_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(expected_model.coef_, model.weights)

    def test_bayesian_regression_persistence(self):
        model = BayesianRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)
    
    def test_rigde_regression(self):
        model = RidgeRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        calculated_y = model.predict(self.predict_x)

        expected_model = Ridge2(alpha=0.01, fit_intercept=False)
        expected_model.fit(self.train_x, self.train_y)
        expected_y = expected_model.predict(self.predict_x)

        np.testing.assert_array_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(expected_model.coef_, model.weights)
    
    def test_rigde_regression_persistence(self):
        model = RidgeRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)

    def test_lasso_regression(self):
        model = LassoRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        calculated_y = model.predict(self.predict_x)

        expected_model = Lasso2(alpha=0.01, fit_intercept=False)
        expected_model.fit(self.train_x, self.train_y)
        expected_y = expected_model.predict(self.predict_x)

        np.testing.assert_array_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(expected_model.coef_, model.weights)


    def test_lasso_regression_persistence(self):
        model = LassoRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)


    def test_huber_regression(self):
        model = HuberRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        calculated_y = model.predict(self.predict_x)

        expected_model = HuberRegressor2(alpha=0.01, fit_intercept=False)
        expected_model.fit(self.train_x, self.train_y)
        expected_y = expected_model.predict(self.predict_x)

        np.testing.assert_array_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(expected_model.coef_, model.weights)


    def test_huber_regression_persistence(self):
        model = HuberRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)

    
    def test_sgd_regression_persistence(self):
        model = SGDRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)


    def test_tweedie_regression(self):
        model = TweedieRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        calculated_y = model.predict(self.predict_x)

        expected_model = TweedieRegressor2(alpha=0.01, fit_intercept=False)
        expected_model.fit(self.train_x, self.train_y)
        expected_y = expected_model.predict(self.predict_x)

        np.testing.assert_array_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(expected_model.coef_, model.weights)

    def test_tweedie_regression_persistence(self):
        model = TweedieRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)


    def test_pa_regression_persistence(self):
        model = PassiveAggressiveRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)


    def test_ths_regression_persistence(self):
        model = TheilSenRegression(features=['a', 'b', 'c'], fit_intercept=False)
        model.fit(self.train_x, self.train_y)

        desc = model.save()
        new_model = load_model(desc)

        calculated_y = new_model.predict(self.predict_x)
        expected_y = model.predict(self.predict_x)

        np.testing.assert_array_almost_equal(calculated_y, expected_y)
        np.testing.assert_array_almost_equal(new_model.weights, model.weights)