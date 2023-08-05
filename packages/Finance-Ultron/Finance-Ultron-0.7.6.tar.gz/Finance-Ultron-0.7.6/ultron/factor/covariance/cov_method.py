# -*- coding: utf-8 -*-
from sklearn.covariance import LedoitWolf,ShrunkCovariance,OAS
from sklearn.model_selection import GridSearchCV
import numpy as np


def unshrunk_cov(ret_tb, window=20):
    cov = np.mat(np.cov(ret_tb.tail(window).T.values).astype(float)) * 250
    return cov

def lwshrunk_cov(ret_tb, window=20):
    lw = LedoitWolf()
    cov = lw.fit(ret_tb.tail(window).values).covariance_ * 250
    return cov

def shrunk_cov(ret_tb, window=20):
    cov = ShrunkCovariance().fit(ret_tb.tail(window).values).covariance_ * 250
    return cov

def gridsearch_cov(ret_tb, window=20):
    tuned_parameters = [{'shrinkage': np.logspace(-1.0, 0, 30)}]
    cov = GridSearchCV(ShrunkCovariance(), tuned_parameters).fit(
        ret_tb.tail(window).values).best_estimator_.covariance_ * 250
    return cov

def oas_cov(ret_tb, window=20):
    return OAS().fit(ret_tb.tail(window).values).covariance_ * 250