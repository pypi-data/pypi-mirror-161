from ultron.utilities.logger import kd_logger
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.winsorize import winsorize_normal
from ultron.tradingday import *
import numpy as np
import pandas as pd
import copy,pdb,math
import warnings
warnings.filterwarnings("ignore")


class MultipleFactor(object):
    def __init__(self, signal_data=None, volatility_data=None, returns_data=None):
        self._signal_data = signal_data
        self._volatility_data = volatility_data
        self._returns_data = returns_data

    def _weighted(self, data, equal=0, name='risk'):
        if equal == 0:
            weighted = data[[name]] / data[[name]].sum()
            weighted['code'] = data['code'].values
        
        else:
            weighted =  1 / len(data)
            weighted = pd.DataFrame([weighted for i in range(0, len(data))],
                                columns=[name],
                                index=data.index)
        weighted['code'] = data['code'].values
        weighted = weighted.reset_index().drop(['trade_date'],axis=1)
        return weighted.rename(columns={name:'weight'})

    def _mixed_signal(self, columns):
        mixed_signal = copy.deepcopy(self._signal_data)
        mixed_signal['signal'] = np.nanmean(mixed_signal.set_index(['trade_date','code'])[columns],axis=1)
        mixed_signal = mixed_signal[['trade_date','code','signal']]
        ### 过滤叠加信号为Nan
        mixed_signal = mixed_signal.dropna(subset=['signal'])
        return mixed_signal

    def _transformer(self, signal):
        s = copy.deepcopy(signal).sort_values(by=['signal'])
        equal = s[s['signal'] == 0]
        nequal = s[s['signal'] != 0]
        le = len(nequal)
        short = nequal[:int(le/2)]
        long = nequal[int(le/2):]
        short['signal'] = short['signal'].apply(lambda x: x if x < 0 else  0-x)
        long['signal'] = long['signal'].apply(lambda x: x if x > 0 else 0-x)
        return pd.concat([long,short,equal],axis=0).sort_values(
            by=['signal']).reset_index(drop=True)

    def _symmetry(self, mixed_signal):
        signal = mixed_signal.set_index('trade_date').groupby(
            level=['trade_date']).apply(lambda x: self._transformer(x))
        return signal.reset_index().drop(['level_1'],axis=1)

    def _initialize_weight(self, mixed_signal, volatility_name):
        data = mixed_signal.merge(
            self._volatility_data, on=['trade_date','code'])
        data['risk'] = data['signal'] / data[volatility_name]

        ## 权重归一化
        #weighted = data.set_index(['trade_date']).groupby(level=['trade_date']).apply(
        #    lambda x: self._weighted(x)).reset_index()
        #weighted = weighted[['trade_date','weight','code']]
        ### 多空组合，归零处理
        long_weighted = data[data.risk > 0][['trade_date','code','risk']] ## 多头权重
        short_weighted = data[data.risk < 0][['trade_date','code','risk']]## 空头权重
        equal_weighted = data[data.risk == 0][['trade_date','code','risk']] ### 0 权重
        long_weighted = long_weighted.set_index(['trade_date']).groupby(
            level=['trade_date']).apply(
                lambda x: self._weighted(data=x, equal=0, name='risk')
            ).reset_index()[['trade_date','weight','code']]


        short_weighted = short_weighted.set_index(['trade_date']).groupby(
            level=['trade_date']).apply(
                lambda x: self._weighted(data=x, equal=0, name='risk')
                ).reset_index()[['trade_date','weight','code']]
        short_weighted['weight'] = 0 - short_weighted['weight']

        equal_weighted = equal_weighted[['trade_date','risk','code']].rename(
            columns={'risk':'weight'}
        )
        ### 数据合并
        weighted = long_weighted.append(short_weighted).append(equal_weighted)
        weighted['trade_date'] = pd.to_datetime(weighted['trade_date'])
        return weighted

    def _returns_corr(self, returns):
        return returns.set_index(['trade_date','code'])['nxt1_ret'].unstack().corr(
            method='spearman')

    def _winsorize_volatility(self, name, volatility_data):
        cols = [name]
        diff_cols = [col for col in volatility_data.columns if col not in cols]
        grouped = volatility_data.groupby(['trade_date']) 
        alpha_res = []
        for k, g in grouped:
            new_factors = factor_processing(g[cols].values,
                    pre_process=[winsorize_normal])
            f = pd.DataFrame(new_factors, columns=cols)
            for k in diff_cols:
                f[k] = g[k].values
            alpha_res.append(f)
        return pd.concat(alpha_res).sort_values(by=['trade_date','code'])


    def _weighted_normalised(self, target_pos, windows):
        sum_weighted = target_pos.groupby(level=['trade_date']).apply(
            lambda x: x['weight'].abs().sum())
        ma_weighted = sum_weighted.rolling(windows).mean()
        ma_weighted = (ma_weighted/2).fillna(0.5)
        ma_weighted.name = 'coeff'
        ### 滚动权重
        ma_weighted = ma_weighted.reset_index()
        v = target_pos.dropna(subset=['weight']).reset_index().merge(
            ma_weighted, on=['trade_date'],how='left')
        v['weight'] = v['weight'] * v['coeff']
        v = v.drop(['coeff'],axis=1).set_index(['trade_date','code'])
        return v

    ### 权重计算
    def weighted_run(self, columns=None, default_volatility=0.1, volatility_name='STD20D', period=20, 
                    is_symmetry=True, windows=60):
        kd_logger.info("starting construction")
        columns = columns if columns is not None else [col for col in self._signal_data.columns if col \
            not in ['trade_date','code']]
        mixed_signal = self._mixed_signal(columns)
        if is_symmetry:
            mixed_signal = self._symmetry(mixed_signal)
            
        kd_logger.info("initialize weight")

        weighted = self._initialize_weight(mixed_signal, volatility_name)
        
        weighted = weighted.sort_values(by=['trade_date','code'])
        weighted['trade_date'] = pd.to_datetime(weighted['trade_date'])

        returns_data = self._returns_data.sort_values(by=['trade_date','code'])
        returns_data['trade_date'] = pd.to_datetime(self._returns_data['trade_date'])

        mixed_signal['trade_date'] = pd.to_datetime(mixed_signal['trade_date'])
        mixed_signal = mixed_signal.sort_values(by=['trade_date','code'])

        ### 波动率去极值
        kd_logger.info("volatility winsorize")
        volatility_data = self._winsorize_volatility(
            volatility_data=self._volatility_data, name=volatility_name) #self._volatility_data.sort_values(by=['trade_date','code'])
        volatility_data['trade_date'] = pd.to_datetime(volatility_data['trade_date'])
        weighted_groups = weighted.groupby('trade_date')
        res = []
        for ref_date, this_data in weighted_groups:
            begin_date = advanceDateByCalendar('china.sse', ref_date, '-{0}b'.format(period))
            end_date = advanceDateByCalendar('china.sse', ref_date, '-0b')
            kd_logger.info("begin_date: {0}, end_date: {1}".format(begin_date, end_date))
            signal = mixed_signal.set_index('trade_date').loc[end_date]
            volatility = volatility_data.set_index('trade_date').loc[end_date]
            returns = returns_data.set_index(
                'trade_date').loc[begin_date:end_date].reset_index()
            codes = set(signal.code.unique().tolist()) & set(
                returns.code.unique().tolist()) & set(volatility.code.unique().tolist())
            returns = returns.set_index('code').loc[codes].reset_index()
            signal = signal.set_index('code').loc[codes].reset_index()
            w = copy.deepcopy(this_data)
            #kd_logger.info("calc returns correlation begin_date:{0}, end_date:{1}".format(
            #    begin_date, end_date))
            corr_dt = self._returns_corr(returns).fillna(0)

            ###重置w, 波动率顺序
            w = w.set_index('code').reindex(corr_dt.index).reset_index()
            volatility = volatility.set_index('code').reindex(corr_dt.index).reset_index()
            data = w.merge(corr_dt,on=['code']).merge(volatility, on=['code'])
            cols = [col for col in data.columns if col not in ['code','signal','trade_date',
                                'weight',volatility_name]]
            #kd_logger.info("calc target volatility")
            s = data['weight'] * data[volatility_name]
            v = data[volatility_name]
            n = np.dot(s.T,data[cols])
            if n.shape[0] != s.shape[0]:
                print(n.shape[0], n.shape[0])
            else:
                m = np.dot(n,s)
                if m ==0:
                    continue
                #op = 1 / (s/v).sum() * m
                op = math.sqrt(m)
                weighted_data = copy.deepcopy(this_data)
                weighted_data['weight'] = ((default_volatility / op) * this_data['weight'])
                res.append(weighted_data.set_index(['trade_date','code']))
        target_pos = pd.concat(res,axis=0)
        return target_pos.reset_index() if not windows > 0 else self._weighted_normalised(
            target_pos,windows).reset_index()


    
    def equal_run(self, columns=None, equal=1,is_symmetry=True):
        kd_logger.info("starting construction")
        columns = columns if columns is not None else [col for col in self._signal_data.columns if col \
            not in ['trade_date','code']]
        mixed_signal = self._mixed_signal(columns)
        if is_symmetry:
            mixed_signal = self._symmetry(mixed_signal)
        ###权重换算
        long_signal = mixed_signal[mixed_signal.signal > 0]
        short_signal = mixed_signal[mixed_signal.signal < 0]
        equal_signal = mixed_signal[mixed_signal.signal == 0]

        ## weight
        long_weighted = long_signal.set_index(['trade_date']).groupby(
            level=['trade_date']).apply(
                lambda x: self._weighted(data=x, equal=equal, name='signal')
            ).reset_index()[['trade_date','weight','code']]

        short_weighted = short_signal.set_index(['trade_date']).groupby(
            level=['trade_date']).apply(
                lambda x: self._weighted(data=x, equal=equal, name='signal')
            ).reset_index()[['trade_date','weight','code']]

        equal_weighted = equal_signal[['trade_date', 'code']]
        equal_weighted['weight'] = 0.0
        short_weighted['weight'] = 0 - short_weighted['weight']
        weighted = long_weighted.append(short_weighted).append(equal_weighted)
        weighted['trade_date'] = pd.to_datetime(weighted['trade_date'])
        return weighted

    ### 收益计算
    def returns_run(self, target_position, forward_returns):
        data = pd.concat([target_position,forward_returns],axis=1, join='inner')
        target_position = target_position.reindex(data.dropna().index)
        forward_returns = forward_returns.reindex(data.dropna().index)
        weights = target_position.reindex(forward_returns.index)['weight']
        leverags = weights.groupby('trade_date').apply(sum)
        weighted_returns = (np.exp(forward_returns['nxt1_ret']) - 1).multiply(weights, axis=0)
        factor_ret_se = weighted_returns.groupby(level='trade_date').sum()
        factor_ret_se = np.log(1 + factor_ret_se)
        return factor_ret_se,leverags,weights