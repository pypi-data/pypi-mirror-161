# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pdb,copy
import ultron.factor.empyrical as empyrical
from ultron.strategy.executor.naive import NaiveExecutor
from ultron.optimize.riskmodel import FullRiskModel
from ultron.factor.covariance.cov_engine import CovEngine
from ultron.factor.experimental.portfolio import er_portfolio_analysis
from ultron.optimize.model.linearmodel import ConstLinearModel
from ultron.optimize.constraints import LinearConstraints, \
    create_box_bounds, BoundaryType
from ultron.tradingday import *
from ultron.utilities.logger import kd_logger

def create_params(**kwargs):
    turn_over_target = 1.0 if 'turn_over_target' not in kwargs else kwargs['turn_over_target']
    target_vol = 0.1 if 'target_vol' not in kwargs else kwargs['target_vol']
    lbound = 0. if 'lbound' not in kwargs else kwargs['lbound']
    ubound = 0.04 if 'ubound' not in kwargs else kwargs['ubound']
    cov_windows = 20 if 'cov_windows' not in kwargs else kwargs['cov_windows']
    benchmark_lower = 1.001 if 'benchmark_lower' not in kwargs else kwargs['benchmark_lower']
    benchmark_upper = 0.8 if 'benchmark_upper' not in kwargs else kwargs['benchmark_upper']
    total_lower = -0.001 if 'total_lower' not in kwargs else kwargs['total_lower']
    total_upper = 0.01 if 'total_upper' not in kwargs else kwargs['total_upper']
    effective_industry_lower = -0.20 if 'effective_industry_lower' not in kwargs else kwargs['effective_industry_lower']
    effective_industry_upper = 0.20 if 'effective_industry_upper' not in kwargs else kwargs['effective_industry_upper']
    invalid_industry_lower = -0.20 if 'invalid_industry_lower' not in kwargs else kwargs['invalid_industry_lower']
    invalid_industry_upper = 0.20 if 'invalid_industry_upper' not in kwargs else kwargs['invalid_industry_upper']
    weights_bandwidth = 0.1 if 'weights_bandwidth' not in kwargs else kwargs['weights_bandwidth']
    cov_method = 'unshrunk' if 'cov_method' not in kwargs else kwargs['cov_method']
    method = 'fmv' if 'method' not in kwargs else kwargs['method']
    effective_codes = [] if 'effective_codes' not in kwargs else kwargs['effective_codes']
    invalid_codes = [] if 'invalid_codes' not in kwargs else kwargs['invalid_codes']
    other_boundary = 'absolute' if 'other_boundary' not in kwargs else kwargs['other_boundary']
    benchmark_boundary = 'absolute' if 'benchmark_boundary' not in kwargs else kwargs['benchmark_boundary']
    total_boundary = 'absolute' if 'total_boundary' not in kwargs else kwargs['total_boundary']
    effective_industry_boundary = 'absolute' if 'effective_industry_boundary' not in kwargs else kwargs['effective_industry_boundary']
    invalid_industry_boundary = 'absolute' if 'invalid_industry_boundary' not in kwargs else kwargs['invalid_industry_boundary']
    is_benchmark = 0 if 'is_benchmark' not in kwargs else kwargs['is_benchmark']

    params = {}
    params['industry'] = {}
    params['riskstyle'] = {}

    params['industry']['effective'] = effective_codes
    params['industry']['invalid'] = invalid_codes
    params['riskstyle']['effective'] = []
    params['riskstyle']['invalid'] = []

    params['setting_params'] = {}
    params['setting_params']['weights_bandwidth'] = weights_bandwidth
    params['setting_params']['method'] = method
    params['setting_params']['turn_over_target'] = turn_over_target
    params['setting_params']['target_vol'] = target_vol
    params['setting_params']['cov_windows'] = cov_windows
    params['setting_params']['cov_method'] = cov_method
    params['setting_params']['lbound'] = lbound
    params['setting_params']['ubound'] = ubound
    params['setting_params']['is_benchmark'] = is_benchmark

    params['setting_params']['benchmark'] = {}
    params['setting_params']['total'] = {}
    params['setting_params']['other'] = {}

    ###
    
    params['setting_params']['other']['boundary'] = other_boundary
    params['setting_params']['other']['lower'] = -0.3
    params['setting_params']['other']['upper'] = 0.3

    # benchmark 区间设置
    params['setting_params']['benchmark']['boundary'] = benchmark_boundary
    params['setting_params']['benchmark']['lower'] = benchmark_lower
    params['setting_params']['benchmark']['upper'] = benchmark_upper

    # total 区间设置   条件6
    params['setting_params']['total']['boundary'] = total_boundary
    params['setting_params']['total']['lower'] = total_lower
    params['setting_params']['total']['upper'] = total_upper

    ### 此处考虑行业择时
    params['setting_params']['effective_industry'] = {}
    params['setting_params']['invalid_industry'] = {}

    #### effective_industry 上限行业区间设置
    params['setting_params']['effective_industry']['boundary'] = effective_industry_boundary
    params['setting_params']['effective_industry']['lower'] = effective_industry_lower
    params['setting_params']['effective_industry']['upper'] = effective_industry_upper

    #### invalid_industry 下限行业区间设置
    params['setting_params']['invalid_industry']['boundary'] = invalid_industry_boundary
    params['setting_params']['invalid_industry']['lower'] = invalid_industry_lower
    params['setting_params']['invalid_industry']['upper'] = invalid_industry_upper
    return params


class RunningSetting(object):
    def __init__(self,
                 lbound=None,
                 ubound=None,
                 weights_bandwidth=None,
                 rebalance_method='risk_neutral',
                 bounds=None,
                 **kwargs):
        self.lbound = lbound
        self.ubound = ubound
        self.weights_bandwidth = weights_bandwidth
        self.rebalance_method = rebalance_method
        self.bounds = bounds
        self.more_opts = kwargs

class Strategy(object):
    def __init__(self,
                 alpha_model,
                 start_date=None,
                 end_date=None,
                 risk_model=None,
                 total_data=None,):
        self.start_date = start_date
        self.end_date = end_date
        self.alpha_model = alpha_model
        self.risk_model = risk_model 
        self.total_data = total_data
        if self.total_data is not None:
            self.total_data['trade_date'] = pd.to_datetime(self.total_data['trade_date'])
    
    def prepare_backtest_data(self):
        pass

    def prepare_backtest_models(self, factor_name='factor'):
        models = {}
        total_data_groups = self.total_data.groupby('trade_date')
        alpha_model = ConstLinearModel(features=[factor_name], 
                                weights={factor_name: 1.0})
        for ref_date, _ in total_data_groups:
            models[ref_date] = alpha_model
        self.alpha_models = models
        kd_logger.info("alpha models training finished ...")
    
    def prepare_risk_model(self, name='unshrunk', window=20):
        models = {}
        returns_data = self.total_data[['trade_date', 'code', 'pev1_ret']]
        returns_data = returns_data.set_index(['trade_date','code']).unstack()
        returns_data_groups = returns_data.groupby('trade_date')
        for ref_date, _ in returns_data_groups:
            if ref_date < self.start_date:
                continue
            ref_begin_date = advanceDateByCalendar('china.sse', ref_date, '-{0}b'.format(window))
            ref_end_date = advanceDateByCalendar('china.sse', ref_date, '-0b')
            rtb = returns_data.loc[ref_begin_date:ref_end_date].fillna(0)
            cov = CovEngine.calc_cov(name=name, ret_tb=rtb, window=window)
            model = FullRiskModel(cov)
            models[ref_date] = model
        self.risk_model = models

    def _build_setting(self, neutralized_styles, effective_industry,
                       invalid_industry, setting_params):
        _boundary = {'absolute':BoundaryType.ABSOLUTE,
                     'relative':BoundaryType.RELATIVE}
        constraint_risk = neutralized_styles
        b_type = []
        l_val = []
        u_val = []
        total_risk_names = constraint_risk + ['benchmark', 'total']
        for name in total_risk_names:
            if name == 'benchmark':
                b_type.append(_boundary[setting_params['benchmark']['boundary']])
                l_val.append(setting_params['benchmark']['lower'])
                u_val.append(setting_params['benchmark']['upper'])
            elif name == 'total':
                b_type.append(_boundary[setting_params['total']['boundary']])
                l_val.append(setting_params['total']['lower'])
                u_val.append(setting_params['total']['upper'])
            elif name in effective_industry:
                b_type.append(_boundary[setting_params['effective_industry']['boundary']])
                l_val.append(setting_params['effective_industry']['lower'])
                u_val.append(setting_params['effective_industry']['upper'])
            elif name in invalid_industry:
                b_type.append(_boundary[setting_params['invalid_industry']['boundary']])
                l_val.append(setting_params['invalid_industry']['lower'])
                u_val.append(setting_params['invalid_industry']['upper'])
            else:
                b_type.append(_boundary[setting_params['other']['boundary']])
            l_val.append(setting_params['other']['lower'])
            u_val.append(setting_params['other']['upper'])
        bounds = create_box_bounds(total_risk_names, b_type, l_val, u_val)
        return RunningSetting(
            bounds=bounds, lbound=setting_params['lbound'],
            ubound=setting_params['ubound'],
            weights_bandwidth=setting_params['weights_bandwidth'],
            rebalance_method=setting_params['method'],
            cov_winodws=setting_params['cov_windows'],
            cov_method=setting_params['cov_method'],
            target_vol = setting_params['target_vol'],
            is_benchmark = setting_params['is_benchmark'],
            turn_over_target=setting_params['turn_over_target'])

    @staticmethod
    def _create_lu_bounds(running_setting, codes, benchmark_w):

        codes = np.array(codes)

        if running_setting.weights_bandwidth:
            lbound = np.maximum(0., benchmark_w - running_setting.weights_bandwidth)
            ubound = running_setting.weights_bandwidth + benchmark_w

        lb = running_setting.lbound
        ub = running_setting.ubound

        if lb or ub:
            if not isinstance(lb, dict):
                lbound = np.ones_like(benchmark_w) * lb
            else:
                lbound = np.zeros_like(benchmark_w)
                for c in lb:
                    lbound[codes == c] = lb[c]

                if 'other' in lb:
                    for i, c in enumerate(codes):
                        if c not in lb:
                            lbound[i] = lb['other']
            if not isinstance(ub, dict):
                ubound = np.ones_like(benchmark_w) * ub
            else:
                ubound = np.ones_like(benchmark_w)
                for c in ub:
                    ubound[codes == c] = ub[c]

                if 'other' in ub:
                    for i, c in enumerate(codes):
                        if c not in ub:
                            ubound[i] = ub['other']
        return lbound, ubound

    def _calculate_pos(self, running_setting, er, data, constraints, 
                        benchmark_w, lbound, ubound, risk_model,
                        current_position, is_benchmark=0):
        more_opts = running_setting.more_opts
        try:
            target_pos, _ = er_portfolio_analysis(
                er=er,industry=data.industry_code.values,
                dx_return=None,constraints=constraints,
                detail_analysis=False, benchmark=benchmark_w,
                method=running_setting.rebalance_method,
                lbound=lbound,ubound=ubound,
                current_position=current_position,
                target_vol=more_opts.get('target_vol'),
                turn_over_target=more_opts.get('turn_over_target'),
                risk_model=risk_model)
        except Exception:
            kd_logger.error('{0} rebalance error'.format(data.trade_date.values[0]))
            target_pos = current_position if not is_benchmark else benchmark_w
            target_pos = pd.DataFrame(target_pos,columns=['weight'])
            target_pos['industry'] = data.industry_code.values
            target_pos['er'] = er
        return target_pos
        
    ### 创建仓位持仓权重
    def create_positions(self, params):
        kd_logger.info("starting re-balance ...")
        total_data = copy.deepcopy(self.total_data)
        total_data = total_data if total_data is not None else copy.deepcopy(self.total_data)
        is_in_benchmark = (total_data.weight != 0.).astype(float).values.reshape((-1, 1))
        total_data.loc[:, 'benchmark'] = is_in_benchmark
        total_data.loc[:, 'total'] = np.ones_like(is_in_benchmark)
        total_data_groups = self.total_data.groupby('trade_date')
        previous_pos = pd.DataFrame()
        positions = pd.DataFrame()

        running_setting = self._build_setting(
            neutralized_styles=params['industry']['effective'] + params['industry']['invalid'],
            effective_industry=params['industry']['effective'],
            invalid_industry=params['industry']['invalid'],
            setting_params=params['setting_params'])
        kd_logger.info("running setting finished ...")
        

        if self.alpha_model is None:
            self.prepare_backtest_models()
        
        if self.risk_model is None:
            self.prepare_risk_model(
                name=running_setting.more_opts['cov_method'],
                window=running_setting.more_opts['cov_winodws'])

        is_benchmark = running_setting.more_opts['is_benchmark']  \
                    if 'is_benchmark' in running_setting.more_opts else 0
                    
        for ref_date, this_data in total_data_groups:
            if ref_date < self.start_date:
                continue
            new_model = self.alpha_models[ref_date]
            risk_model = self.risk_model[ref_date]
            codes = this_data.code.values.tolist()

            if previous_pos.empty:
                prev_date = advanceDateByCalendar('china.sse', ref_date, '-1b')
                current_position = self.total_data.set_index(
                    'trade_date').loc[prev_date].weight.values
            else:
                previous_pos.set_index('code', inplace=True)
                remained_pos = previous_pos.reindex(codes)
                remained_pos.fillna(0., inplace=True)
                current_position = remained_pos.weight.values
            benchmark_w = this_data.weight.values
            constraints = LinearConstraints(running_setting.bounds,
                                            this_data,
                                            benchmark_w)
            lbound, ubound = self._create_lu_bounds(running_setting, codes, benchmark_w)
            this_data.fillna(0, inplace=True)
            ###是否标准化
            new_factors = this_data[new_model.features].values
            new_factors = pd.DataFrame(new_factors, columns=['factor'], index=codes)
            er = new_model.predict(new_factors).astype(float)

            kd_logger.info('{0} re-balance: {1} codes'.format(ref_date, len(er)))
            target_pos = self._calculate_pos(
                running_setting=running_setting, er=er, 
                data=this_data, constraints=constraints, 
                benchmark_w=benchmark_w, lbound=lbound, 
                ubound=ubound,risk_model=risk_model.get_risk_profile(codes),
                current_position=current_position,
                is_benchmark=is_benchmark)
            target_pos['code'] = codes
            target_pos['trade_date'] = ref_date
            target_pos['benchmark'] = benchmark_w
            positions = positions.append(target_pos)
            previous_pos = target_pos
        return positions

    def matcher(self, ret_df):
        rets = []
        def match(returns, turnover=0, period=empyrical.DAILY):
            returns = returns.astype('float').dropna()
            annual_return = empyrical.annual_return(returns=returns,period=period)
            annual_volatility = empyrical.annual_volatility(returns=returns,period=period)
            cagr = empyrical.cagr(returns=returns,period=period)
            sharpe_ratio = empyrical.sharpe_ratio(returns=returns,period=period)
            downside_risk = empyrical.downside_risk(returns=returns,period=period)
            max_drawdown = empyrical.max_drawdown(returns=returns)
            results = {'annual_return':annual_return, 'annual_volatility':annual_volatility,
                'cagr':cagr,'sharpe_ratio':sharpe_ratio,'downside_risk':downside_risk,
                'max_drawdown':max_drawdown,'calmar_ratio':-annual_return/max_drawdown}
            if turnover > 0. : results['turnover'] = turnover
            return results
        for r in ['returns','benchmark_returns','excess_return']:
            turnover = ret_df['turn_over'].mean() if r == 'returns' else 0
            mat = match(ret_df[r], turnover=turnover)
            mat['name'] = r
            rets.append(mat)
        return rets



    def backtest(self, positions, returns_data, rate):
        kd_logger.info("starting backting ...")
        executor = NaiveExecutor()
        total_data = positions.merge(
            returns_data[['trade_date','code','nxt1_ret']],on=['trade_date','code'])
        total_data_groups = total_data.groupby('trade_date')
        rets = []
        b_rets = []
        turn_overs = []
        leverags = []
        for ref_date,this_data in total_data_groups:
            turn_over, executed_pos = executor.execute(this_data)
            leverage = executed_pos.weight.abs().sum()
            ret = executed_pos.weight.values @ (np.exp(this_data.nxt1_ret.values) - 1.) - len(this_data.code) * rate * turn_over
            b_ret = executed_pos.benchmark.values @ (np.exp(this_data.nxt1_ret.values) - 1.) - len(this_data.code) * rate * turn_over
            rets.append(np.log(1. + ret))
            b_rets.append(np.log(1. + b_ret))
            executor.set_current(executed_pos)
            turn_overs.append(turn_over)
            leverags.append(leverage)
            kd_logger.info('{0}: turn over {1}, returns {2}, benchmark returns {3}'.format(
                ref_date, round(turn_over,4), round(ret,4), round(b_ret,4)))
        trade_dates = positions.trade_date.unique()
        ret_df = pd.DataFrame({'returns': rets, 'turn_over': turn_overs, 'leverage': leverags,
                       'benchmark_returns': b_rets}, index=trade_dates)
        ret_df['excess_return'] = ret_df['returns'] - ret_df['benchmark_returns'] * ret_df['leverage']
        return ret_df

    def run(self, params, rate=0.0):
        positions = self.create_positions(params)
        returns_data = self.total_data[['trade_date', 'code', 'nxt1_ret']]
        ret_df = self.backtest(positions, returns_data, rate)
        match_df = self.matcher(ret_df)
        ret_df.loc[advanceDateByCalendar('china.sse', ret_df.index[-1], '1b')] = 0.
        ret_df = ret_df.shift(1)
        ret_df.iloc[0] = 0.
        return match_df, ret_df,positions