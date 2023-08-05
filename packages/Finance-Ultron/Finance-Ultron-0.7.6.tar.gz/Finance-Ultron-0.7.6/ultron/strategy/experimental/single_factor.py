import code
from tokenize import group
from ultron.factor.experimental.normalize import rolling_groups
from ultron.factor.analysis.quantile_analysis import er_quantile_analysis
from ultron.factor.data.quantile import quantile
from ultron.tradingday import *
import numpy as np
import pandas as pd
import pdb, copy
class SingleFactor(object):
    def __init__(self, factor_data, market_data, codes, columns):
        self._factor_data = factor_data
        self._market_data = market_data
        self._codes = codes
        self._columns = columns

    def returns(self, market_data, period):
        price_tb = market_data['closePrice'].unstack()
        price_tb.fillna(method='pad', inplace=True)
        return_tb = np.log(price_tb.shift(-period) / price_tb)
        return_tb = return_tb.replace([np.inf, -np.inf], np.nan)
        return_tb = return_tb.stack().reindex(market_data.index)
        return_tb.name = 'nxt1_ret'
        return return_tb.reset_index()

    def normalize(self, factor_data, windows, columns):
        #normalize_data = factor_data.set_index('code').groupby(level=['code']).apply(
        #        lambda x: rolling_groups(x,columns, windows))
        #normalize_data = normalize_data.reset_index().drop(['level_1'],axis=1)
        rolling_data = factor_data.set_index(['trade_date','code']).unstack().rolling(windows)
        current_data = factor_data.set_index(['trade_date','code']).unstack()
        normalize_data = (current_data - rolling_data.mean()) / rolling_data.std()
        normalize_data = normalize_data.stack(dropna=True)
        normalize_data = normalize_data.sort_values(by=['trade_date','code']).fillna(0)
        return normalize_data.reset_index()

    
    def _transformer(self, normalize_data, returns, columns, period):
        begin_date = normalize_data.trade_date.min()
        end_date = normalize_data.trade_date.max()
        dates = makeSchedule(begin_date, end_date,  str(period)+'b', 'china.sse', 
                            BizDayConventions.Preceding)
        dates = [d.strftime('%Y-%m-%d') for d in dates]
        dt = normalize_data.trade_date.dt.strftime('%Y-%m-%d').unique().tolist()
        dates = set(dt) & set(dates)
        normalize_data = normalize_data.set_index('trade_date').loc[dates].sort_values(
            by=['trade_date']).reset_index()
        normalize_data['trade_date'] = pd.to_datetime(normalize_data['trade_date'])
        returns['trade_date'] = pd.to_datetime(returns['trade_date'])
        total_data = returns.merge(normalize_data, on=['trade_date','code'], how='left')
        total_data = total_data.set_index(
            ['trade_date','code'])[columns].unstack().fillna(
                method='pad').stack().reset_index()
        return total_data

    def quantile_analysis(self, normalize_data, factor_name, n_bins, de_trend=False):
        df = pd.DataFrame(columns=['q' + str(i) for i in range(1, n_bins+1)])
        grouped = normalize_data.groupby('trade_date')
        for k, g in grouped:
            er = g[factor_name].values
            dx_return = g['nxt1_ret'].values
            res = er_quantile_analysis(er, n_bins=n_bins, dx_return=dx_return, de_trend=de_trend)
            df.loc[k, :] = res
        df['q'] = df['q'+str(n_bins)]-df['q1']
        return df
    
    def quantile(self, normalize_data, factor_name, n_bins):
        grouped = normalize_data.groupby('trade_date')
        res = []
        for k, g in grouped:
            o = copy.deepcopy(g)
            t = copy.deepcopy(o)
            o = o.dropna(subset=[factor_name])
            o['group'] = quantile(o[factor_name], n_bins) + 1
            o = t.merge(o[['code','trade_date','group']], on=['trade_date','code'], how='left')
            res.append(o.set_index(['trade_date','code']))
        group_dt = pd.concat(res,axis=0)
        return group_dt


    def run(self, codes=None, columns=[], windows=10, period=1, n_bins=5, 
            normalize_data=None, returns_data=None):
        print('start single factor analysis...')
        if len(columns) == 0:
            columns = self._columns
        if normalize_data is None:
            print('start data normalize...')
            normalize_data = self.normalize(factor_data=self._factor_data, windows=windows, 
                            columns=columns)
        normalize_data = self._factor_data
        if returns_data is None:
            print('start data returns...')
            returns_data = self.returns(self._market_data.set_index(['trade_date','code']), 
                            period)
        if codes is None:
            codes = self._codes
            
        normalize_data['trade_date'] = pd.to_datetime(normalize_data['trade_date'])
        returns_data['trade_date'] = pd.to_datetime(returns_data['trade_date'])
        total_data = normalize_data.merge(returns_data, on=['trade_date','code'])
        
        ### 指定品种
        codes = list(set(total_data['code'].unique().tolist()) & set(codes))
        total_data = total_data.set_index('code').loc[codes].reset_index()
        qt_res = []
        for col in columns:
            print("start {0} quantile ...".format(col))
            df = self.quantile(normalize_data[['code','trade_date', col]], col, n_bins)
            qt_res.append({'name':col, "qdata":df})

        qa_res = []
        for col in columns:
            print("start {0} quantile analysis...".format(col))
            df = self.quantile_analysis(normalize_data=total_data, 
                    factor_name=col, n_bins=n_bins)
            qa_res.append({'name':col, "qdata":df})
        return qt_res, qa_res
        

