from typing import Union
import cvxpy as cp
import numpy as np
from ultron.optimize.pfopt.base import _IOptimizer

class LpOptimizer(_IOptimizer):
    def __init__(self,
                cost: np.ndarray,
                cons_matrix: np.ndarray = None,
                lower_bound: Union[float, np.ndarray] = None,
                upper_bound: Union[float, np.ndarray] = None):
        super().__init__(cost, cons_matrix, lower_bound, upper_bound)
    
    def solver(self, solver: str = "CBC"):
        x, constraints = self._prepare()

        constraints.append(sum(x) == 0.0) # 总权重之和为0.0的限制条件
        prob = cp.Problem(cp.Minimize(x @ self._cost), constraints=constraints)
        prob.solve(solver=solver)
        return x.value, prob.value, prob.status

class L1LpOptimizer(_IOptimizer):
    def __init__(self,
                 cost: np.ndarray,
                 benchmark: np.ndarray,
                 l1norm: float,
                 cons_matrix: np.ndarray = None,
                 lower_bound: Union[float, np.ndarray] = None,
                 upper_bound: Union[float, np.ndarray] = None):
        super().__init__(cost, cons_matrix, lower_bound, upper_bound)
        self._benchmark = benchmark
        self._l1norm = l1norm
    
    def solver(self, solver: str = "ECOS"):
        x, constraints = self._prepare()
        constraints.append(
            cp.pnorm(x - self._benchmark, 1) <= self._l1norm
        )
        constraints.append(cp.pnorm(x, 1) <= 2.0) # 限制多头总和为1、空头总和为-1，即相加为2.0
        constraints.append(sum(x) == 0.0) # 总权重之和为0.0的限制条件
        prob = cp.Problem(cp.Minimize(x @ self._cost), constraints=constraints)
        prob.solve(solver=solver)
        return x.value, prob.value, prob.status

    