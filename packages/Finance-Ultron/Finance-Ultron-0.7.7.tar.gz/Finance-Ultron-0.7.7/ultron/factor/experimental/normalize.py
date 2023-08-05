import numpy as np
import pandas as pd
import pdb
from ultron.factor.data.standardize import standardize
from ultron.factor.data.processing import factor_processing

def rolling_standard(x, name, res):
    y = x.values.reshape(x.values.shape[0],1)
    values = factor_processing(y, pre_process=[standardize])
    values = pd.Series(values.reshape(x.values.shape[0],), x.index)
    values.name = name
    res.append(values.reset_index().to_dict(orient='records')[-1])
    return 1


def rolling_groups(data, columns, windows=10):
    alpha_res = []
    for col in columns:
        res = []
        _ = data.set_index('trade_date')[[col]].rolling(windows).apply(
            lambda x: rolling_standard(x, col, res))
        values = pd.DataFrame(res).set_index(['trade_date'])
        alpha_res.append(values)
    return pd.concat(alpha_res,axis=1).reset_index()