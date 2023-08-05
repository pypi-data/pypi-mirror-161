# -*- coding: utf-8 -*-
import pandas as pd
from . cov_method import (
    unshrunk_cov, lwshrunk_cov, shrunk_cov, gridsearch_cov, oas_cov)

func_dict = {'unshrunk':unshrunk_cov, 'lwshrunk':lwshrunk_cov,
            'shrunk':shrunk_cov, 'gridsearch':gridsearch_cov, 
            'oas':oas_cov}

class CovEngine(object):
    @classmethod
    def create_engine(cls, ce_name):
        return func_dict[ce_name]

    @classmethod
    def calc_cov(cls, name, ret_tb, window=20, is_pandas=True):
        cov = func_dict[name](ret_tb=ret_tb, window=window)
        if not is_pandas:
            return cov
        codes = ret_tb.columns.get_level_values(1).unique()
        return pd.DataFrame(data=cov,index=codes,columns=codes)