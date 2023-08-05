# -*- coding: utf-8 -*-
from typing import Optional
import numpy as np
import pandas as pd
from ultron.factor.utilities import agg_mean
from ultron.factor.data.quantile import quantile
from ultron.factor.data.standardize import standardize
from ultron.factor.data.winsorize import winsorize_normal
from ultron.factor.data.processing import factor_processing


def quantile_analysis(factors: pd.DataFrame,
                      factor_weights: np.ndarray,
                      dx_return: np.ndarray,
                      n_bins: int=5,
                      risk_exp: Optional[np.ndarray]=None,
                      **kwargs):

    if 'pre_process' in kwargs:
        pre_process = kwargs['pre_process']
        del kwargs['pre_process']
    else:
        pre_process = [winsorize_normal, standardize]

    if 'post_process' in kwargs:
        post_process = kwargs['post_process']
        del kwargs['post_process']
    else:
        post_process = [standardize]

    er = factor_processing(factors.values, pre_process, risk_exp, post_process) @ factor_weights
    return er_quantile_analysis(er, n_bins, dx_return, **kwargs)


def er_quantile_analysis(er: np.ndarray,
                         n_bins: int,
                         dx_return: np.ndarray,
                         de_trend=False) -> np.ndarray:

    er = er.flatten()
    q_groups = quantile(er, n_bins)

    if dx_return.ndim < 2:
        dx_return.shape = -1, 1

    group_return = agg_mean(q_groups, dx_return).flatten()
    total_return = group_return.sum()
    ret = group_return.copy()

    if de_trend:
        resid = n_bins - 1
        res_weight = 1. / resid
        for i, value in enumerate(ret):
            ret[i] = (1. + res_weight) * value - res_weight * total_return

    return ret