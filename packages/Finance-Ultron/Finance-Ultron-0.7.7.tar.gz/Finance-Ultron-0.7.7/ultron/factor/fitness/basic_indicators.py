import numpy as np
import pandas as pd
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.standardize import standardize
from ultron.factor.data.winsorize import winsorize_normal
from ultron.factor.data.neutralize import neutralize
from ultron.factor.combine.kutil import calc_ic
import pdb


class IC_Weighted(object):
    def __init__(self, result_type):
        self._result_type = result_type
        self._industry_styles = ['Bank','RealEstate','Health','Transportation','Mining',
                                 'NonFerMetal','HouseApp','LeiService','MachiEquip','BuildDeco',
                                 'CommeTrade','CONMAT','Auto','Textile','FoodBever','Electronics',
                                 'Computer','LightIndus','Utilities','Telecom','AgriForest','CHEM',
                                 'Media','IronSteel','NonBankFinan','ELECEQP','AERODEF','Conglomerates']
        self._risk_styles = ['BETA','MOMENTUM','SIZE','EARNYILD','RESVOL','GROWTH','BTOP',
                             'LEVERAGE','LIQUIDTY','SIZENL']
        
        
    #暂时写此处，去极值
    def winsorize(self, total_data, method='sigma', limits=(3.0, 3.0), drop=True):
        se = total_data.copy()
        if method == 'quantile':
            down, up = se.quantile([limits[0], 1.0 - limits[1]])
        elif method == 'sigma':
            std, mean = se.std(), se.mean()
            down, up = mean - limits[0]*std, mean + limits[1]*std
        
        if drop:
            se[se<down] = np.NaN
            se[se>up] = np.NaN
        else:
            se[se<down] = down
            se[se>up] = up
        return se
    
    #中性化
    def neutralize(self, se, risk_df):
        se_index = se.index
        se = se.dropna()
        risk = risk_df.loc[se.index]

        # use numpy for neu, which is faster
        x = np.linalg.lstsq(risk.values, np.matrix(se).T, rcond=None)[0]
        se_neu = se - risk.dot(x)[0]
    
        # # use statsmodels for neu
        # x = risk.values
        # y = se.values
        # model = sm.OLS(y, x)
        # results = model.fit()
        # se_neu = pd.Series(data=y - x.dot(results.params), index=se.index)
        
        return se_neu.reindex(se_index)
    
    #标准化
    def standardize(self, total_data):
        try:
            res = (total_data - np.nanmean(total_data)) / np.nanstd(total_data)
        except:
            res = pd.Series(data=np.NaN, index=total_data.index)
        return res
    
    
    def ic_calc(self, factor_data, forward_returns, risk_data, factor_name,
            risk_styles = None, method='quantile', up_limit=0.025, down_limit=0.025,
            return_col_name='nxt1_ret',ic_type='spearman'):
        fac_list = [factor_name]
        factors_se = factor_data.merge(risk_data.reset_index(), on=['code','trade_date'])
        ndiff_field =  [i for i in list(set(factors_se.columns)) if i not in fac_list]
        risk_styles = self._risk_styles if risk_styles is None else risk_styles
        alpha_res = []
        grouped = factors_se.groupby(['trade_date'])
        for k, g in grouped:
            ret_preprocess = neutralize(g[self._industry_styles + risk_styles].values.astype(float),
                                factor_processing(g[fac_list].fillna(0).values,
                                                  pre_process=[winsorize_normal, standardize]))
            f = pd.DataFrame(ret_preprocess, columns=fac_list)
            for k in ndiff_field:
                f[k] = g[k].values
            alpha_res.append(f)
        factor_se = pd.concat(alpha_res).set_index(['trade_date','code'])[fac_list]
        forward_returns = forward_returns.set_index(['trade_date','code'])
        return calc_ic(factor_df=factor_se.reset_index(), return_df=forward_returns, 
            factor_list=fac_list, return_col_name=return_col_name, ic_type=ic_type)


    def run(self, factor_data, forward_returns, risk_data, factor_name, is_neutralize=True,
            risk_styles = None, method='quantile', up_limit=0.025, down_limit=0.025,
            return_col_name='nxt1_ret',ic_type='spearman'):
        ic_serliaze = self.ic_calc(factor_data=factor_data,forward_returns=forward_returns,
                                  risk_data=risk_data,factor_name=factor_name,
                                  risk_styles=risk_styles,method=method,up_limit=up_limit,
                                  down_limit=down_limit,return_col_name=return_col_name,
                                  ic_type=ic_type)[factor_name].dropna()
        return ic_serliaze.values.mean() if self._result_type=='ic' else ic_serliaze.values.mean() / ic_serliaze.values.std()
