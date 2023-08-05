import os,time, pdb
import datetime as dt
import sqlalchemy
import numpy as np
import pandas as pd
import statsmodels.api as sm
from alphamind.data.processing import factor_processing
from alphamind.data.standardize import standardize
from alphamind.data.winsorize import winsorize_normal
from alphamind.data.neutralize import neutralize

class HighFrequencyWeighted(object):
    def __init__(self):
        self._industry_styles = ['Bank','RealEstate','Health','Transportation','Mining',
                                 'NonFerMetal','HouseApp','LeiService','MachiEquip','BuildDeco',
                                 'CommeTrade','CONMAT','Auto','Textile','FoodBever','Electronics',
                                 'Computer','LightIndus','Utilities','Telecom','AgriForest','CHEM',
                                 'Media','IronSteel','NonBankFinan','ELECEQP','AERODEF','Conglomerates']
        self._risk_styles = ['BETA','MOMENTUM','SIZE','EARNYILD','RESVOL','GROWTH','BTOP',
                             'LEVERAGE','LIQUIDTY','SIZENL']
    
    '''  
    def top_equal_weights(self, group, top='top', top_pct=0.2):
        if top == 'bottom':
            group = -1.0 * group
        group = group.rank(pct=True)
        group[group < 1.0-top_pct] = 0.0
        group[group >= 1.0-top_pct] = 1.0 / len(group[group >= 1.0-top_pct])
        return group
    
    def returns(self, factor_se, forward_returns, init_capital=100000):
        # 超额收益，此处benchmark采用全股票池算数均值
        forward_excess_returns = forward_returns.groupby(level=['trade_date']).apply(
            lambda x: x - x.mean())
        res_dict = {}
        for top in ['top', 'bottom']:
            weights = factor_se.groupby(level=['trade_date']).apply(lambda x: self.top_equal_weights(x, top=top, top_pct=0.2))
            weighted_returns = forward_excess_returns.multiply(weights, axis=0)
            factor_ret_se = weighted_returns.groupby(level='trade_date').sum()
            turnover_se = weights.unstack().diff().abs().sum(axis=1)
            res_dict[top] = pd.DataFrame({'returns': factor_ret_se, 'turnover': turnover_se})
        return res_dict
        
        
    def stats_information(self, price_res_dict, horizon):
        stats_df = pd.DataFrame({x: self.calc_stats(price_res_dict[x], horizon) for x in price_res_dict.keys()}).T
        stats_df.index.name = 'top_bot'
        #stats_df = stats_df.reset_index()
        return stats_df
    '''
    
    def to_weights(self, group):
        demeaned_vals = group - group.mean()
        return demeaned_vals / demeaned_vals.abs().sum()
    
    def to_ls_count(self, group, long=True):
        demeaned_vals = group - group.mean()
        if long:
            count = len(demeaned_vals[demeaned_vals>0])
        else:
            count = len(demeaned_vals[demeaned_vals<0])
        return count 
    
    def returns(self, factor_se, forward_returns):
        weights = factor_se.groupby(level=['trade_date']).apply(self.to_weights)
        weighted_returns = forward_returns.multiply(weights, axis=0)
        
        factor_ret_se = weighted_returns.groupby(level='trade_date').sum()
        turnover_se = weights.unstack().diff().abs().sum(axis=1)
        long_count = factor_se.groupby(level=['trade_date']).apply(self.to_ls_count)
        short_count = factor_se.groupby(level=['trade_date']).apply(lambda x: self.to_ls_count(x, long=False))
        #计算方向
        forward_returns.name='nxt1_ret'
        factor_se.name = 'factor'
        forward_returns.reset_index().merge(factor_se.reset_index(),on=['trade_date','code'])
        ic_mean = forward_returns.reset_index().merge(factor_se.reset_index(),
                                            on=['trade_date','code']).groupby('trade_date').apply(
            lambda x: np.corrcoef(x['factor'], x['nxt1_ret'])[0, 1]).mean()
        direction = np.sign(ic_mean)
        return factor_ret_se, turnover_se, long_count, short_count, direction
    
    def calc_stats(self, returns_df, turnover_df, direction, horizon):
        # 总体指标
        returns_se, turnover_se = returns_df, turnover_df
        #纯多头组合可以考虑费率，多空组合不能考虑费率，若为负收益率(反方向因子),再减费率不符合逻辑
        #returns_se = returns_se - turnover_se * 0.001
        
        ir = returns_se.mean() / returns_se.std()
        sharpe = np.sqrt(252 / horizon) * ir
        turnover = turnover_se.mean()
        returns = returns_se.sum() * 252 / horizon / len(returns_se)
        fitness = sharpe * np.sqrt(abs(returns) / turnover)
        margin = returns_se.sum() / turnover_se.sum()
        stats_se = pd.Series({'status':1, 'ir': ir, 'sharpe': sharpe, 'turnover': turnover, 
                              'returns': returns, 'fitness': fitness, 'margin': margin,
                              'direction':direction,
                              'score':abs(sharpe)})
        return stats_se
        
    def run(self, factor_data, risk_data, mkt_df, default_value,
            factor_name, is_neutralize = True, risk_styles = None, horizon=1, 
            keys='bar30_vwap', method='quantile', up_limit=0.025, down_limit=0.025,
            init_capital=100000):
        """
        参数：
            horizon: 调仓期，按照交易日计算。
        """
        fac_list = [factor_name]
        factors_se = factor_data.merge(risk_data.reset_index(), on=['code','trade_date'])
        ndiff_field =  [i for i in list(set(factors_se.columns)) if i not in fac_list]
        risk_styles = self._risk_styles if risk_styles is None else risk_styles
        alpha_res = []
        grouped = factors_se.groupby(['trade_date'])
        for k, g in grouped:
            if is_neutralize:
                ret_preprocess = neutralize(g[self._industry_styles + risk_styles].values.astype(float),
                                factor_processing(g[fac_list].fillna(0).values,
                                                  pre_process=[winsorize_normal, standardize]))
            else:
                ret_preprocess = factor_processing(g[fac_list].fillna(0).values,
                                                  pre_process=[winsorize_normal, standardize])
            f = pd.DataFrame(ret_preprocess, columns=fac_list)
            for k in ndiff_field:
                f[k] = g[k].values
            alpha_res.append(f)
        factor_se = pd.concat(alpha_res).set_index(['trade_date','code'])[factor_name]
        mkt_se = mkt_df.set_index(['trade_date','code'])
        price_tb = mkt_se[keys].unstack()
        return_tb = (price_tb.shift(-horizon) / price_tb - 1.0)
        return_tb[return_tb>10.0] = np.NaN
        return_tb = return_tb.shift(-1)
        return_se = return_tb.stack()
        #  多空计算因子收益数据
        factor_ret_se, turnover_se, long_count, short_count, direction = self.returns(
            factor_se, return_se)
        return self.calc_stats(factor_ret_se, turnover_se, direction, horizon)
        # top 20% 等权方法计算的因子收益数据
        '''
        price_res_dict = self.returns(factor_se, return_se)
        stats_df = self.stats_information(price_res_dict, horizon)
        if stats_df.loc['top'].score > stats_df.loc['bottom'].score:# and stats_df.loc['top'].score > 0:
            return stats_df.loc['top'].to_dict()
        elif stats_df.loc['bottom'].score > stats_df.loc['top'].score:# and stats_df.loc['bottom'].score > 0:
            return stats_df.loc['bottom'].to_dict()
        else:
            return {'status':0, 'score':default_value}
        '''
