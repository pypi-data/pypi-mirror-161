# -*- coding: utf-8 -*-

from sklearn.svm import NuSVR
from ultron.optimize.model.modelbase import create_model_base


class NvSVRModel(create_model_base('sklearn')):

    def __init__(self, features=None, fit_target=None, **kwargs):
        super().__init__(features=features, fit_target=fit_target)
        self.impl = NuSVR(**kwargs)