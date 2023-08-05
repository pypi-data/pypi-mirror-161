# -*- coding: utf-8 -*-

import unittest

from ultron.optimize.model.linearmodel import ConstLinearModel

class ModelBase(unittest.TestCase):
    def test_simple_model_features(self):
        model = ConstLinearModel(features=['c', 'b', 'a'])
        self.assertListEqual(['a', 'b', 'c'], model.features)
