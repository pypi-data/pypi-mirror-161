# -*- coding: utf-8 -*-

from typing import Tuple
from typing import Union

import numpy as np

from .optimizers import LPOptimizer
from .optimizers import L1LPOptimizer



def linear_builder(er: np.ndarray,
                   lbound: Union[np.ndarray, float] = None,
                   ubound: Union[np.ndarray, float] = None,
                   risk_constraints: np.ndarray = None,
                   risk_target: Tuple[np.ndarray, np.ndarray] = None,
                   turn_over_target: float = None,
                   current_position: np.ndarray = None,
                   method: str = "deprecated") -> Tuple[str, np.ndarray, np.ndarray]:
    er = er.flatten()

    if risk_constraints is not None:
        risk_lbound = risk_target[0].reshape((-1, 1))
        risk_ubound = risk_target[1].reshape((-1, 1))
        cons_matrix = np.concatenate((risk_constraints.T, risk_lbound, risk_ubound), axis=1)
    else:
        cons_matrix = None

    if not turn_over_target or current_position is None:
        prob = LPOptimizer(-er, cons_matrix, lbound, ubound)

        if prob.status() == "optimal" or prob.status() == 'optimal_inaccurate':
            return prob.status(), prob.feval(), prob.x_value()
        else:
            raise (prob.status())
    elif turn_over_target:
        prob = L1LPOptimizer(objective=-er,
                             cons_matrix=cons_matrix,
                             current_pos=current_position,
                             target_turn_over=turn_over_target,
                             lbound=lbound,
                             ubound=ubound)

        if prob.status() == 'optimal' or prob.status() == 'optimal_inaccurate':
            return prob.status(), prob.feval(), prob.x_value()
        else:
            raise (prob.status())
