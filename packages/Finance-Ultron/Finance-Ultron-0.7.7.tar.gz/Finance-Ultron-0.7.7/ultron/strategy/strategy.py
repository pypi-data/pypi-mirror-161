# -*- coding: utf-8 -*-

from ultron.strategy.fut_strategy import Strategy as FutStrategy
from ultron.strategy.stk_strategy import Strategy as StkStrategy

func_dict = {'fut':FutStrategy,'stk':StkStrategy}
class StrategyEngine(object):
    @classmethod
    def create_class(cls, name):
        return func_dict[name] if name in func_dict else None