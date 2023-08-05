from .stats import (aggregate_returns, annual_return, annual_volatility, cagr,
                    calmar_ratio, cum_returns, cum_returns_final,
                    downside_risk, excess_sharpe, max_drawdown, omega_ratio,
                    roll_annual_volatility, roll_max_drawdown,
                    roll_sharpe_ratio, roll_sortino_ratio, sharpe_ratio,
                    simple_returns, sortino_ratio, tail_ratio, _adjust_returns)

from .periods import (DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY)

import numpy as np


def turnover(data,
             factor_name,
             key=['trade_date', 'code'],
             groupby_key='trade_date'):

    def to_weights(group):
        demeaned_vals = group - group.mean()
        return demeaned_vals / demeaned_vals.abs().sum()

    weights = data.set_index(key)[[
        factor_name
    ]].groupby(level=groupby_key).apply(to_weights)
    turnover_se = weights.unstack().diff().abs().sum(axis=1)
    return turnover_se.mean()


def fitness(returns_se, turnover=None, horizon=1):
    ir = returns_se.mean() / returns_se.std()
    sharpe = np.sqrt(252 / horizon) * ir
    returns = returns_se.sum() * 252 / horizon / len(returns_se)
    fitness = sharpe * np.sqrt(abs(returns) / turnover)
    return fitness


#def fitnesss(rets, turnover):
#    returns = factor_ret.sum()*252/horizon/len(factor_ret)
#    fitness = sharpe * np.sqrt(abs(returns)/turnover)
