# -*- coding: utf-8 -*-
from asyncio import constants
from typing import Union
import cvxpy as cp
import numpy as np
import pdb

class TargetVarianceOptimizer(object):
    def __init__(self,
                cost: np.ndarray,
                benchmark: np.ndarray,
                l1norm: float,
                variance_target: float,
                variance: np.ndarray = None,
                lower_bound: Union[float, np.ndarray] = None,
                upper_bound: Union[float, np.ndarray] = None):
        self._n = len(cost)
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._l1norm = l1norm
        self._variance = variance
        self._variance_target = variance_target
        self._benchmark = benchmark
        self._cost = cost
    
    def _prepare(self):
        x = cp.Variable(self._n)
        constraints = []
        if self._lower_bound is not None:
            constraints.append(x >= self._lower_bound)
        if self._upper_bound is not None:
            constraints.append(x <= self._upper_bound)
        return x, constraints



    def solver(self, solver: str= "ECOS"):
        x, constraints = self._prepare()
        risk = cp.quad_form(x, self._variance)
        constraints.append(
            cp.pnorm(x - self._benchmark, 1) <= self._l1norm
        )
        constraints.append(cp.pnorm(x, 1) <= 2.0)
        constraints.append(risk <= self._variance_target)

        constraints.append(sum(x) == 0.0)

        prob = cp.Problem(cp.Minimize(x @ self._cost),
                        constraints=constraints)
        prob.solve(solver=solver)
        return x.value, prob.value, prob.status
        