# -*- coding: utf-8 -*-
import numpy as np
from .linear import L1LpOptimizer as _L1LpOptimizer
from .linear import LpOptimizer as _LpOptimizer
from .quadratic import TargetVarianceOptimizer as _TargetVarianceOptimizer

class LPOptimizer:
    def __init__(self,
                 objective: np.array,
                 cons_matrix: np.ndarray,
                 lbound: np.ndarray,
                 ubound: np.ndarray,
                 method: str = "deprecated"):

        self._optimizer = _LpOptimizer(cost=objective,
                                       cons_matrix=cons_matrix,
                                       lower_bound=lbound,
                                       upper_bound=ubound)
        self._x, self._f_eval, self._status = self._optimizer.solver(solver="ECOS")

    def status(self):
        return self._status

    def feval(self):
        return self._f_eval

    def x_value(self):
        return self._x

class L1LPOptimizer:

    def __init__(self,
                 objective: np.array,
                 cons_matrix: np.ndarray,
                 current_pos: np.ndarray,
                 target_turn_over: float,
                 lbound: np.ndarray,
                 ubound: np.ndarray):
        self._optimizer = _L1LpOptimizer(cost=objective,
                                         benchmark=current_pos,
                                         l1norm=target_turn_over,
                                         cons_matrix=cons_matrix,
                                         lower_bound=lbound,
                                         upper_bound=ubound)
        self._x, self._f_eval, self._status = self._optimizer.solver()

    def status(self):
        return self._status

    def feval(self):
        return self._f_eval

    def x_value(self):
        return self._x


class TargetVarianceOptimizer:
    def __init__(self, 
                objective: np.array,
                current_pos: np.array,
                target_turn_over: float,
                target_vol: float,
                cov: np.ndarray,
                lbound: np.ndarray,
                ubound: np.ndarray) -> None:
        self._optimizer = _TargetVarianceOptimizer(cost=objective,
                benchmark=current_pos, l1norm=target_turn_over,
                variance_target=target_vol*target_vol, variance=cov,
                lower_bound=lbound,upper_bound=ubound)
        self._x, self._f_val,self._status = self._optimizer.solver()

    def status(self):
        return self._status
    
    def feval(self):
        return self._f_val
    
    def x_value(self):
        return self._x