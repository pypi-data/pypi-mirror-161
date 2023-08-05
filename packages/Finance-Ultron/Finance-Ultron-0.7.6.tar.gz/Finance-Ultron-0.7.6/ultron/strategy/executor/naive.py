# -*- coding: utf-8 -*-

from typing import Tuple
import pandas as pd
from ultron.strategy.executor.base import Base

class NaiveExecutor(Base):
    def __init__(self):
        super(NaiveExecutor, self).__init__()
    
    def execute(self, target_pos: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
        if self.current_pos.empty:
            turn_over = target_pos.weight.abs().sum()
        else:
            turn_over = self.calc_turn_over(target_pos, self.current_pos)
        self.current_pos = target_pos.copy()
        return turn_over, target_pos
