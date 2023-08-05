# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pdb,copy
import ultron.factor.empyrical as empyrical
from ultron.strategy.executor.naive import NaiveExecutor
from ultron.utilities.logger import kd_logger
from ultron.tradingday import *
from ultron.factor.analysis.factor_analysis import er_portfolio_analysis
from ultron.factor.othgnz.othgnz_engine import OthgnzEngine
from ultron.factor.combine.combine_engine import CombineEngine
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.standardize import standardize
from ultron.factor.data.winsorize import winsorize_normal
from ultron.optimize.model.linearmodel import ConstLinearModel
from ultron.optimize.constraints import LinearConstraints, \
    create_box_bounds, BoundaryType


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
    effective_industry_lower = 0.0 if 'effective_industry_lower' not in kwargs else kwargs['effective_industry_lower']
    effective_industry_upper = 0.20 if 'effective_industry_upper' not in kwargs else kwargs['effective_industry_upper']
    invalid_industry_lower = 0.0 if 'invalid_industry_lower' not in kwargs else kwargs['invalid_industry_lower']
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
    period = 0 if 'period' not in kwargs else kwargs['period']
    is_benchmark = 0 if 'is_benchmark' not in kwargs else kwargs['is_benchmark']
    neutralized_styles = None if 'neutralized_styles' not in kwargs else kwargs['neutralized_styles']
    synthetize_opts =  {}  if 'synthetize_opts' not in kwargs else kwargs['synthetize_opts']

    params = {}
    params['industry'] = {}
    params['riskstyle'] = {}

    params['industry']['effective'] = effective_codes
    params['industry']['invalid'] = invalid_codes
    params['riskstyle']['effective'] = []
    params['riskstyle']['invalid'] = []

    params['setting_params'] = {}
    params['setting_params']['period'] = period
    params['setting_params']['weights_bandwidth'] = weights_bandwidth
    params['setting_params']['method'] = method
    params['setting_params']['turn_over_target'] = turn_over_target
    params['setting_params']['target_vol'] = target_vol
    params['setting_params']['cov_windows'] = cov_windows
    params['setting_params']['cov_method'] = cov_method
    params['setting_params']['lbound'] = lbound
    params['setting_params']['ubound'] = ubound
    params['setting_params']['neutralized_styles'] = neutralized_styles
    params['setting_params']['is_benchmark'] = is_benchmark

    params['setting_params']['synthetize_opts'] = synthetize_opts

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
                 neutralized_styles=None,
                 **kwargs):
        self.lbound = lbound
        self.ubound = ubound
        self.weights_bandwidth = weights_bandwidth
        self.rebalance_method = rebalance_method
        self.bounds = bounds
        self.neutralized_styles = neutralized_styles
        self.more_opts = kwargs


class Strategy(object):
    def __init__(self,
                 alpha_model,
                 features=None,
                 start_date=None,
                 end_date=None,
                 risk_model=None,
                 total_data=None):
        self.start_date = start_date
        self.end_date = end_date
        self.alpha_models = alpha_model
        self.risk_models = risk_model 
        self.total_data = total_data
        self.featrues = features
        if self.total_data is not None:
            self.total_data['trade_date'] = pd.to_datetime(self.total_data['trade_date'])

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
        except Exception as e:
            kd_logger.error('{0} rebalance error. {1}'.format(data.trade_date.values[0], str(e)))
            target_pos = current_position if not is_benchmark else benchmark_w
            target_pos = pd.DataFrame(target_pos,columns=['weight'])
            target_pos['industry'] = data.industry_code.values
            target_pos['er'] = er
        return target_pos

    def prepare_backtest_models(self, factor_name='factor'):
        models = {}
        total_data_groups = self.total_data.groupby('trade_date')
        alpha_model = ConstLinearModel(features=[factor_name], 
                                weights={factor_name: 1.0})
        for ref_date, _ in total_data_groups:
            models[ref_date] = alpha_model
        self.alpha_models = models
        kd_logger.info("alpha models training finished ...")

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
            period = setting_params['period'],
            synthetize_opts=setting_params['synthetize_opts'],
            turn_over_target=setting_params['turn_over_target'])

    def _industry_median(self, standard_data, factor_name):
        median_values = standard_data[['trade_date',
                                 'industry_code','code',factor_name]].groupby(
            ['trade_date','industry_code']).median()[factor_name]
        median_values.name = factor_name + '_median'
        factor_data = standard_data[['trade_date','industry_code',
                                 'code',factor_name]].merge(
                                    median_values.reset_index(),
                                    on=['trade_date','industry_code'], how='left')
        factor_data['standard_' + factor_name] = factor_data[factor_name].mask(pd.isnull(
            factor_data[factor_name]),factor_data[factor_name + '_median'])
        return factor_data.drop([factor_name + '_median'],axis=1).set_index(
            ['trade_date','code','industry_code'])

    def _returs_impl(self, price_data, key, name, direction=1): #1 后置收益率  -1 前置收益率
        price_tb = price_data[key].unstack()
        price_tb.fillna(method='pad', inplace=True)
        return_tb = np.log(price_tb.shift(-1) / price_tb) if direction == 1 else np.log(price_tb / price_tb.shift(1))
        return_tb = return_tb.replace([np.inf, -np.inf], np.nan)
        return_tb = return_tb.stack().reindex(price_data.index)
        return_tb.name = name
        return return_tb

    def create_factors(self, factors_data, params):
        method = params['method']
        if method == 'equal':
            kd_logger.info('synthetize method:{0}'.format(method))
            equal_combine = CombineEngine.create_engine('equal_combine')
            factors_df = factors_data.copy(deep=True)
            factors_df['factor'] = equal_combine(factors_df, self.featrues)
            equal_data = factors_df.copy(deep=True).drop(self.featrues,axis=1).sort_values(by=['trade_date','code'])
            equal_data['trade_date'] = pd.to_datetime(equal_data['trade_date'])
            return equal_data[['code','trade_date','factor','nxt1_ret']]
        elif method == 'ic_equal':
            kd_logger.info('synthetize method:{0}, span:{1}'.format(method, params['span']))
            span = params['span']
            hist_ic_combine = CombineEngine.create_engine('hist_ic_combine')
            factors_df = factors_data.copy(deep=True)
            ic_equal, hist_ret = hist_ic_combine(factors_df[['trade_date','code'] + self.featrues], 
                                    factors_df[['trade_date','code','nxt1_ret']],
                                             self.featrues, span=span, method='equal')
            ic_equal = ic_equal.rename(columns={'combine':'factor'}).merge(
                factors_df[['trade_date','code','nxt1_ret']], 
                on=['trade_date','code']).sort_values(by=['trade_date','code'])
            ic_equal['trade_date'] = pd.to_datetime(ic_equal['trade_date'])
            return ic_equal
        elif method == 'ic_half':
            kd_logger.info('synthetize method:{0}, span:{1}, half_life:{2}'.format(method, params['span'], params['half_life']))
            hist_ic_combine = CombineEngine.create_engine('hist_ic_combine')
            span = params['span']
            half_life = params['half_life']
            factors_df = factors_data.copy(deep=True)
            ic_half, hist_ret = hist_ic_combine(factors_df[['trade_date','code'] + self.featrues], 
                                        factors_df[['trade_date','code','nxt1_ret']], 
                self.featrues, span=span, method='half_life', half_life=half_life)
            ic_half = ic_half.rename(columns={'combine':'factor'}).merge(
                factors_df[['trade_date','code','nxt1_ret']], 
                on=['trade_date','code']).sort_values(by=['trade_date','code']).sort_values(
                    by=['trade_date','code'])
            ic_half['trade_date'] = pd.to_datetime(ic_half['trade_date'])
            return ic_half
        elif method == 'ret_equal':
            kd_logger.info('synthetize method:{0}, span:{1}'.format(method, params['span']))
            span = params['span']
            hist_ret_combine = CombineEngine.create_engine('hist_ret_combine')
            factors_df = factors_data.copy(deep=True)
            ret_equal, hist_ret = hist_ret_combine(factors_df[['trade_date','code'] + self.featrues],
                        factors_df[['trade_date','code','nxt1_ret']], self.featrues, span=span, method='equal')
            ret_equal = ret_equal.rename(columns={'combine':'factor'}).merge(
                factors_df[['trade_date','code','nxt1_ret']], 
                on=['trade_date','code']).sort_values(by=['trade_date','code'])
            ret_equal['trade_date'] = pd.to_datetime(ret_equal['trade_date'])
            return ret_equal
        elif method == 'ret_half':
            kd_logger.info('synthetize method:{0}, span:{1}, half_life:{2}'.format(method, params['span'], params['half_life']))
            span = params['span']
            half_life = params['half_life']
            hist_ret_combine = CombineEngine.create_engine('hist_ret_combine')
            factors_df = factors_data.copy(deep=True)
            ret_half, hist_ret = hist_ret_combine(factors_df[['trade_date','code'] + self.featrues],
                                      factors_df[['trade_date','code','nxt1_ret']],
                                      self.featrues, span=span, method='half_life', half_life=half_life)
            ret_half = ret_half.rename(columns={'combine':'factor'}).merge(
                factors_df[['trade_date','code','nxt1_ret']],
                on=['trade_date','code']).sort_values(by=['trade_date','code'])
            ret_half['trade_date'] = pd.to_datetime(ret_half['trade_date'])
            return ret_half
        elif method == 'max_ic_sample':
            kd_logger.info('synthetize method:{0}, span:{1}, weight_limit:{2}'.format(
                method, params['span'], params['weight_limit']))
            max_ic_combine = CombineEngine.create_engine('max_ic_combine')
            span = params['span']
            weight_limit = True if params['weight_limit'] == 1 else False # 是否约束权重为正
            factors_df = factors_data.copy(deep=True)
            sample_ir_df, hist_ic = max_ic_combine(factors_df[['trade_date','code'] + self.featrues],
                            factors_df[['trade_date','code','nxt1_ret']], self.featrues, 
                            span=span, method='sample', weight_limit=weight_limit)
            sample_ir_df = sample_ir_df.rename(columns={'combine':'factor'}).merge(
                factors_df[['trade_date','code','nxt1_ret']],
                on=['trade_date','code']).sort_values(by=['trade_date','code'])
            return sample_ir_df
        elif method == 'max_ic_shrunk':
            kd_logger.info('synthetize method:{0}, span:{1}, weight_limit:{2}'.format(
                method, params['span'], params['weight_limit']))
            max_ic_combine = CombineEngine.create_engine('max_ic_combine')
            span = params['span']
            weight_limit = True if params['weight_limit'] == 1 else False # 是否约束权重为正
            factors_df = factors_data.copy(deep=True)
            shrunk_ir_df, hist_ic = max_ic_combine(factors_df[['trade_date','code'] + self.featrues],
                            factors_df[['trade_date','code','nxt1_ret']], self.featrues, 
                            span=span, method='shrunk', weight_limit=weight_limit)
            shrunk_ir_df = shrunk_ir_df.rename(columns={'combine':'factor'}).merge(
                factors_df[['trade_date','code','nxt1_ret']],
                on=['trade_date','code']).sort_values(by=['trade_date','code'])
            return shrunk_ir_df

    def standardize_data(self):
        kd_logger.info("starting standardize data ...")
        kd_logger.info("running setting finished ...")

        factors_data = copy.deepcopy(self.total_data)[['trade_date','code','industry_code']  + self.featrues]
        res = []
        kd_logger.info("starting industry median data ...")
        for col in self.featrues:
            rts = self._industry_median(factors_data, col)
            res.append(rts)
        factors_data = pd.concat(res,axis=1)
        factors_data = factors_data.fillna(0)
        factors_data = factors_data.reset_index().set_index(['trade_date','code'])
        industry_dummy = pd.get_dummies(factors_data['industry_code'])
        factors_data = pd.concat([factors_data,industry_dummy],axis=1)
        standarad_cols = ['standard_' +  col for col in self.featrues]
        diff_cols = ['trade_date','code', 'industry_code']
        grouped = factors_data.reset_index().groupby(['trade_date'])
        kd_logger.info("starting  factor processing data ...")
        alpha_res = []
        industry_styles = factors_data['industry_code'].unique().tolist()
        for k, g in grouped:
            new_factors = factor_processing(g[standarad_cols].values,
                 pre_process=[winsorize_normal,standardize],
                 risk_factors=g[industry_styles].values.astype(float),
                 post_process=[standardize])
            f = pd.DataFrame(new_factors, columns=standarad_cols)
            for k in diff_cols:
                f[k] = g[k].values
            alpha_res.append(f)
        factors_data = pd.concat(alpha_res)
        factors_data = factors_data.rename(
            columns=dict(zip(standarad_cols, self.featrues)))
        return factors_data

    def serialize_data(self, factors_data):
        kd_logger.info("running setting finished ...")
        market_data = copy.deepcopy(self.total_data)[['trade_date','code','closePrice']]
        next_rets = self._returs_impl(
            market_data.set_index(['trade_date','code']),'closePrice','nxt1_ret').reset_index()
        next_rets['trade_date'] = pd.to_datetime(next_rets['trade_date'])
        kd_logger.info("returns finished ...")
        serialize_data = copy.deepcopy(factors_data).merge(
            next_rets,on=['trade_date','code'])
        return serialize_data

    def synthetize_data(self, serialize_data, params):
        symmetry_othgnz = OthgnzEngine.create_engine('symmetry')
        diff_cols = [col for col in serialize_data.columns if col not in self.featrues]
        factors_data = symmetry_othgnz(copy.deepcopy(serialize_data[diff_cols + self.featrues]).fillna(0), diff_cols).sort_values(by=['trade_date','code'])
        running_setting = self._build_setting(
            neutralized_styles=params['industry']['effective'] + params['industry']['invalid'],
            effective_industry=params['industry']['effective'],
            invalid_industry=params['industry']['invalid'],
            setting_params=params['setting_params'])
        kd_logger.info("running setting finished ...")
        factors_data = self.create_factors(factors_data, running_setting.more_opts['synthetize_opts'])
        return factors_data


    def prepare_backtest_data(self,params):
        standardize_data = self.standardize_data()
        serialize_data = self.serialize_data(standardize_data)
        synthetize_data = self.synthetize_data(serialize_data,params)
        return synthetize_data

    def create_positions(self, params, total_data=None):
        kd_logger.info("starting re-balance ...")
        total_data = total_data if total_data is not None else copy.deepcopy(self.total_data)
        is_in_benchmark = (total_data.weight > 0.).astype(float).values.reshape((-1, 1))
        total_data.loc[:, 'benchmark'] = is_in_benchmark
        total_data.loc[:, 'total'] = np.ones_like(is_in_benchmark)
        total_data_groups = total_data.groupby('trade_date')
        previous_pos = pd.DataFrame()
        positions = pd.DataFrame()

        running_setting = running_setting = self._build_setting(
            neutralized_styles=params['industry']['effective'] + params['industry']['invalid'],
            effective_industry=params['industry']['effective'],
            invalid_industry=params['industry']['invalid'],
            setting_params=params['setting_params'])
        kd_logger.info("running setting finished ...")

        if self.alpha_models is None:
            self.prepare_backtest_models()

        for ref_date, this_data in total_data_groups:
            if ref_date < self.start_date:
                continue
            new_model = self.alpha_models[ref_date]

            risk_model = self.risk_models[ref_date] if self.risk_models is not None else None
            codes = this_data.code.values.tolist()
            
            if previous_pos.empty:
                dates = total_data['trade_date'].dt.strftime('%Y-%m-%d').unique().tolist()
                try:
                    pos = dates.index(ref_date.strftime('%Y-%m-%d'))
                except:
                    pos = 0
                prev_date = dates[pos]
                current_position = total_data.set_index('trade_date').loc[prev_date].weight.values
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
            this_data.fillna(0, inplace=True)
            new_factors = factor_processing(
                this_data[new_model.features].values,
                pre_process=[winsorize_normal,standardize],
                risk_factors=this_data[running_setting.neutralized_styles].values.astype(
                                                float) if running_setting.neutralized_styles else None,
                post_process=[standardize])
            new_factors = pd.DataFrame(new_factors, columns=new_model.features, index=codes)
            er = new_model.predict(new_factors).astype(float)
            kd_logger.info('{0} re-balance: {1} codes'.format(ref_date, len(er)))
            target_pos = self._calculate_pos(running_setting,
                                             er,
                                             this_data,
                                             constraints,
                                             benchmark_w,
                                             lbound,
                                             ubound,
                                             risk_model=risk_model,
                                             current_position=current_position)
            target_pos['code'] = codes
            target_pos['trade_date'] = ref_date
            target_pos['benchmark'] = benchmark_w
            positions = positions.append(target_pos)
            previous_pos = target_pos
        return positions

    def rebalance_positions(self, params):
        total_data = self.prepare_backtest_data(params=params)
        industry_code  = self.total_data[['trade_date','code',
                    'industry_code']].set_index(['trade_date','code'])
        industry_dummy = pd.get_dummies(industry_code['industry_code'])
        factors_data = pd.concat([total_data.set_index(['trade_date','code']),
                                industry_dummy,industry_code],axis=1).sort_values(
                                    by=['trade_date','code'],ascending=True)
        index_constituent = self.total_data[['trade_date','code','weight']].set_index(
            ['trade_date','code'])
        factors_data = pd.concat([factors_data,index_constituent],axis=1)
        positions = self.create_positions(params=params, total_data=factors_data.reset_index())
        return positions
    
    def backtest(self, positions, market_data, rate):
        next_rets = self._returs_impl(
            market_data.set_index(['trade_date','code']),'closePrice','nxt1_ret').reset_index()
        kd_logger.info("starting backting ...")
        executor = NaiveExecutor()
        total_data = positions.merge(
            next_rets[['trade_date','code','nxt1_ret']],on=['trade_date','code'])
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

    def run(self, params,rate=0.0):
        positions = self.rebalance_positions(params)
        market_data = self.total_data[['trade_date','code','closePrice']]
        ret_df = self.backtest(positions, market_data, rate)
        match_df = self.matcher(ret_df)
        return match_df,ret_df,positions

        


