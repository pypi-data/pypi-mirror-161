import numpy as np
import pandas as pd

def factor_coverage_seq(factors_data, factor_name):
    coverage = factors_data.sort_values(by=['trade_date', 'code']).groupby(
        ['trade_date']).apply(
        lambda x: 1 - np.isnan(x[factor_name].values).sum() / len(x))
    coverage.name = factor_name
    return coverage


def code_coverage_seq(factors_data, factors, threshold):
    res = []
    for col in factors:
        rts = factors_data.sort_values(by=['trade_date']).groupby(
            ['trade_date']).apply(
                lambda x: 1 - np.isnan(
                    x[col].values).sum() / len(x))
        res.append(rts)
    coverage = pd.concat(res,axis=1)
    valid_col = (coverage >= threshold).all()
    valid_col = valid_col[valid_col].index
    return len(valid_col)/len(factors)