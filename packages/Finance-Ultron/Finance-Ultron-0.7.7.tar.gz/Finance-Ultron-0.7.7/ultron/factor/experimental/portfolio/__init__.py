# -*- coding: utf-8 -*-
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
import pandas as pd


from ultron.factor.data.processing import factor_processing
from ultron.factor.data.standardize import standardize
from ultron.factor.data.winsorize import winsorize_normal
from ultron.optimize.constraints import Constraints
from ultron.optimize.constraints import LinearConstraints
from ultron.optimize.linearbuilder import linear_builder
from ultron.optimize.longshortbulder import long_short_builder
from ultron.optimize.meanvariancebuilder import mean_variance_builder
from ultron.factor.experimental.portfolio.meanvariancebuilder import mean_variance_builder as f_mean_variance_builder
from ultron.factor.experimental.portfolio.linearbuilder import linear_builder as f_linear_builder
from ultron.factor.analysis.simplesettle import simple_settle


def er_portfolio_analysis(er: np.ndarray,
                          industry: np.ndarray,
                          dx_return: np.ndarray,
                          constraints: Optional[Union[LinearConstraints, Constraints]] = None,
                          detail_analysis=True,
                          benchmark: Optional[np.ndarray] = None,
                          is_tradable: Optional[np.ndarray] = None,
                          method='risk_neutral',
                          **kwargs) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    er = er.flatten()

    def create_constraints(benchmark, **kwargs):
        if 'lbound' in kwargs:
            lbound = kwargs['lbound'].copy()
            del kwargs['lbound']
        else:
            lbound = np.maximum(0., benchmark - 0.01)

        if 'ubound' in kwargs:
            ubound = kwargs['ubound'].copy()
            del kwargs['ubound']
        else:
            ubound = 0.01 + benchmark
        if is_tradable is not None:
            ubound[~is_tradable] = np.minimum(lbound, ubound)[~is_tradable]

        risk_lbound, risk_ubound = constraints.risk_targets()
        cons_exp = constraints.risk_exp
        return lbound, ubound, cons_exp, risk_lbound, risk_ubound

    if method == 'long_risk_neutral':
        lbound, ubound, cons_exp, risk_lbound, risk_ubound = create_constraints(benchmark, **kwargs)

        turn_over_target = kwargs.get('turn_over_target')
        current_position = kwargs.get('current_position')

        status, _, weights = linear_builder(er,
                                            risk_constraints=cons_exp,
                                            lbound=lbound,
                                            ubound=ubound,
                                            risk_target=(risk_lbound, risk_ubound),
                                            turn_over_target=turn_over_target,
                                            current_position=current_position)
        if status not in ("optimal", "optimal_inaccurate"):
            raise ValueError('linear programming optimizer in status: {0}'.format(status))

    elif method == 'ls' or method == 'long_short':
        weights = long_short_builder(er).flatten()
    if method == 'longshort_risk_neutral':
        lbound, ubound, cons_exp, risk_lbound, risk_ubound = create_constraints(benchmark, **kwargs)
        turn_over_target = kwargs.get('turn_over_target')
        current_position = kwargs.get('current_position')
        status, _, weights = f_linear_builder(er,
                                            risk_constraints=cons_exp,
                                            lbound=lbound,
                                            ubound=ubound,
                                            risk_target=(risk_lbound, risk_ubound),
                                            turn_over_target=turn_over_target,
                                            current_position=current_position)
        if status not in ("optimal", "optimal_inaccurate"):
            raise ValueError('linear programming optimizer in status: {0}'.format(status))

    elif method == 'longshort_mean_variance':
        lbound = kwargs['lbound']
        ubound = kwargs['ubound']
        risk_model = kwargs['risk_model']
        turn_over_target = kwargs.get('turn_over_target')
        current_position = kwargs.get('current_position')
        target_vol = kwargs.get('target_vol')
        status, _, weights = mean_variance_builder(er=er,
                                                   risk_model=risk_model,
                                                   current_position=current_position,
                                                   turn_over_target=turn_over_target,
                                                   vol_target=target_vol,
                                                   lbound=lbound,
                                                   ubound=ubound
                                                   )
        if status != 'optimal':
            raise ValueError('mean variance optimizer in status: {0}'.format(status))

    elif method == 'mv' or method == 'long_mean_variance':
        lbound, ubound, cons_exp, risk_lbound, risk_ubound = create_constraints(benchmark, **kwargs)
        risk_model = kwargs['risk_model']

        if 'lam' in kwargs:
            lam = kwargs['lam']
        else:
            lam = 1.

        status, _, weights = mean_variance_builder(er,
                                                   risk_model=risk_model,
                                                   bm=benchmark,
                                                   lbound=lbound,
                                                   ubound=ubound,
                                                   risk_exposure=cons_exp,
                                                   risk_target=(risk_lbound, risk_ubound),
                                                   lam=lam)
        if status != 'optimal':
            raise ValueError('mean variance optimizer in status: {0}'.format(status))

    else:
        raise ValueError("Unknown building type ({0})".format(method))

    if detail_analysis:
        analysis = simple_settle(weights, dx_return, industry, benchmark)
    else:
        analysis = None
    return pd.DataFrame({'weight': weights,
                         'industry': industry,
                         'er': er}), \
           analysis