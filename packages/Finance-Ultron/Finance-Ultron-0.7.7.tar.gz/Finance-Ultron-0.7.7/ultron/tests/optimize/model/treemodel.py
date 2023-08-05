# -*- coding: utf-8 -*-

from imp import new_module
import pdb
import unittest

import numpy as np
import pandas as pd

from ultron.optimize.model.loader import load_model
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
from ultron.optimize.model.treemodel import StackingClassifier
from ultron.optimize.model.treemodel import StackingRegressor
from ultron.optimize.model.treemodel import VotingClassifier
from ultron.optimize.model.treemodel import VotingRegressor
from ultron.optimize.model.linearmodel import LogisticRegression
from ultron.optimize.model.treemodel import XGBClassifier
from ultron.optimize.model.treemodel import XGBRegressor
from ultron.optimize.model.treemodel import XGBTrainer
from ultron.optimize.model.treemodel import LGBMClassifier
from ultron.optimize.model.treemodel import LGBMRegressor
from ultron.optimize.model.treemodel import LGBMTrainer


class TreeModel(unittest.TestCase):

    def setUp(self):
        self.features = list('0123456789')
        self.x = pd.DataFrame(np.random.randn(1000, 10), columns=self.features)
        self.y = np.random.randn(1000)
        self.sample_x = pd.DataFrame(np.random.randn(100, 10), columns=self.features)
        self.sample_y = np.random.randn(100)


    def test_gradinet_boosting_regress_persistence(self):
        model = GradientBoostingRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)


    def test_gradinet_boosting_classify_persistence(self):
        model = GradientBoostingClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)


    
    def test_ada_boost_regress_persistence(self):
        model = AdaBoostRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    
    def test_ada_boost_classify_persistence(self):
        model = AdaBoostClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    
    def test_bagging_regress_persistence(self):
        model = BaggingRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    
    def test_bagging_classify_persistence(self):
        model = BaggingClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)


    
    def test_extra_trees_regress_persistence(self):
        model = ExtraTreesRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)


    def test_extra_trees_classify_persistence(self):
        model = ExtraTreesClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)
    
    def test_random_forest_regress_persistence(self):
        model = RandomForestRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_random_forest_classify_persistence(self):
        model = RandomForestClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_decisiontree_regress_persistence(self):
        model = DecisionTreeRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_decisiontree_classify_persistence(self):
        model = DecisionTreeClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)
    
    '''
    def test_stacking_regressor_persistence(self):
        m1 = RandomForestRegressor(features=self.features)
        m1.fit(self.x, self.y)
        m1_score = m1.score(self.sample_x, self.sample_y)

        m2 = ExtraTreesRegressor(features=self.features)
        m2.fit(self.x, self.y)
        m2_score = m2.score(self.sample_x, self.sample_y)

        m3 = BaggingRegressor(features=self.features)
        m3.fit(self.x, self.y)
        m3_score = m3.score(self.sample_x, self.sample_y)

        m4 = AdaBoostRegressor(features=self.features)
        m4.fit(self.x, self.y)
        m4_score = m4.score(self.sample_x, self.sample_y)


        m5 = GradientBoostingRegressor(features=self.features)
        m5.fit(self.x, self.y)
        m5_score = m1.score(self.sample_x, self.sample_y)

        model = StackingRegressor(features=self.features,
                regressors=[m1.device,  m2.device,
                                m3.device, m4.device, 
                                m5.device],
                    meta_regressor=LogisticRegression().device)
        model.fit(self.x, self.y)
        score = model.score(self.sample_x, self.sample_y)
        scores = np.array([m1_score, m2_score, m3_score, m4_score, m5_score])
        assert(score >= scores.min() - 0.3)

        desc = model.save()

        model1 = load_model(desc)
        score1 = model1.score(self.sample_x, self.sample_y)
        assert(score1 == score)
    '''
    def test_stacking_classify_persistence(self):
        y = np.where(self.y > 0, 1, 0)
        sample_y = np.where(self.sample_y > 0, 1, 0)
        m1 = RandomForestClassifier(features=self.features)
        m1.fit(self.x, y)
        m1_score = m1.score(self.sample_x, sample_y)

        m2 = ExtraTreesClassifier(features=self.features)
        m2.fit(self.x, y)
        m2_score = m2.score(self.sample_x, sample_y)

        m3 = BaggingClassifier(features=self.features)
        m3.fit(self.x, y)
        m3_score = m3.score(self.sample_x, sample_y)

        m4 = AdaBoostClassifier(features=self.features)
        m4.fit(self.x, y)
        m4_score = m4.score(self.sample_x, sample_y)


        m5 = GradientBoostingClassifier(features=self.features)
        m5.fit(self.x, y)
        m5_score = m1.score(self.sample_x, sample_y)

        model = StackingClassifier(features=self.features,
                classifiers=[m1.device,  m2.device,
                                m3.device, m4.device, 
                                m5.device],
                    meta_classifier=LogisticRegression().device)
        model.fit(self.x, y)
        score = model.score(self.sample_x, sample_y)
        scores = np.array([m1_score, m2_score, m3_score, m4_score, m5_score])
        assert(score >= scores.min() - 0.3)

        desc = model.save()

        model1 = load_model(desc)
        score1 = model1.score(self.sample_x, sample_y)
        assert(score1 == score)


    def test_voting_classify_persistence(self):
        y = np.where(self.y > 0, 1, 0)
        sample_y = np.where(self.sample_y > 0, 1, 0)
        m1 = RandomForestClassifier(features=self.features)
        m1.fit(self.x, y)
        m1_score = m1.score(self.sample_x, sample_y)

        m2 = ExtraTreesClassifier(features=self.features)
        m2.fit(self.x, y)
        m2_score = m2.score(self.sample_x, sample_y)

        m3 = BaggingClassifier(features=self.features)
        m3.fit(self.x, y)
        m3_score = m3.score(self.sample_x, sample_y)

        m4 = AdaBoostClassifier(features=self.features)
        m4.fit(self.x, y)
        m4_score = m4.score(self.sample_x, sample_y)


        m5 = GradientBoostingClassifier(features=self.features)
        m5.fit(self.x, y)
        m5_score = m1.score(self.sample_x, sample_y)

        model = VotingClassifier(features=self.features,
                estimators=[('m1', m1.device), ('m2', m2.device),
                ('m3', m3.device), ('m4', m4.device),
                ('m5', m5.device)],voting='soft')

        model.fit(self.x, y)
        score = model.score(self.sample_x, sample_y)
        scores = np.array([m1_score, m2_score, m3_score, m4_score, m5_score])
        assert(score >= scores.min() - 0.3)

        desc = model.save()

        model1 = load_model(desc)
        score1 = model1.score(self.sample_x, sample_y)
        assert(score1 == score)
        

    def test_xgb_regress_persistence(self):
        model = XGBRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_xgb_classify_persistence(self):
        model = XGBClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_xgb_trainer_equal_classifier(self):
        model1 = XGBClassifier(n_estimators=100,
                               learning_rate=0.1,
                               max_depth=3,
                               features=self.features,
                               random_state=42)

        model2 = XGBTrainer(features=self.features,
                            objective='reg:logistic',
                            booster='gbtree',
                            tree_method='exact',
                            n_estimators=100,
                            learning_rate=0.1,
                            max_depth=3,
                            random_state=42)

        y = np.where(self.y > 0, 1, 0)
        model1.fit(self.x, y)
        model2.fit(self.x, y)

        predict1 = model1.predict(self.sample_x)
        predict2 = model2.predict(self.sample_x)
        predict2 = np.where(predict2 > 0.5, 1., 0.)
        np.testing.assert_array_almost_equal(predict1, predict2)

    def test_xgb_trainer_persistence(self):
        model = XGBTrainer(features=self.features,
                           objective='binary:logistic',
                           booster='gbtree',
                           tree_method='hist',
                           n_estimators=200)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_lgbm_regress_persistence(self):
        model = LGBMRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)
    
    def test_lgbm_classify_persistence(self):
        model = LGBMClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)
       
    '''
    def test_lgbm_trainer_persistence(self):
        model = LGBMTrainer(features=self.features,
                             objective='regression',
                             n_estimators=100,
                             learning_rate=0.1,
                             max_depth=3)
        y = np.where(self.y > 0, 1, 0)
        pdb.set_trace()
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)
    '''