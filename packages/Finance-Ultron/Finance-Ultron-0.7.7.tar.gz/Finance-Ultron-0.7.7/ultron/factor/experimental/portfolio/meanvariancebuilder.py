# -*- coding: utf-8 -*-

from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union
import numpy as np

from ultron.utilities.exceptions import PortfolioBuilderException

from .optimizers import (
    TargetVarianceOptimizer
)



def mean_variance_builder(er: np.ndarray,
                risk_model: Dict[str, Union[None, np.ndarray]],
                current_position: np.ndarray,
                vol_target: float,
                turn_over_target: float,
                lbound: Union[np.ndarray, float, None],
                ubound: Union[np.ndarray, float, None],
                ) -> Tuple[str, np.ndarray, np.ndarray]:
    cov = risk_model['cov']
    prob = TargetVarianceOptimizer(objective=-er,
            current_pos=current_position,
            lbound=lbound,ubound=ubound,
            target_vol=vol_target,
            target_turn_over=turn_over_target,
            cov=cov,
            )
    if prob.status() == 'optimal' or prob.status() == 'optimal_inaccurate':
        return prob.status(), prob.feval(), prob.x_value()
    else:
        raise PortfolioBuilderException(prob.status())
