import pandas as pd

def industry_fill(factor_data, factor_sets, index_key=['trade_date','code'],
                  group_key=['trade_date','industry_code'], fill_type='mean'):
    mean_values = factors_data.groupby(group_key).mean()[factor_columns].fillna(0)
    standard_data = factors_data.merge(mean_values.reset_index(),on=group_key, 
                                       how='left',suffixes=('', '_w')).set_index(
                                       index_key)
    mean_columns = [f + '_w'for f in factor_sets]
    factor_res = []
    for f in factor_columns:
        factor_data = standard_data[f].mask(pd.isnull(standard_data[f]),standard_data[f + '_w'])
        factor_res.append(factor_data)
    return pd.concat(factor_res, axis=1)
    
def data_processing(factor_name, total_data, is_ind_neutralize, custom_risk_styles,
                    pre_process=1, post_process=1, is_nansorize=1):
    alpha_res = []
    grouped = total_data.dropna(subset=[factor_name]).groupby(['trade_date']) if is_nansorize else \
                total_data.fillna(0).groupby(['trade_date'])
    ndiff_columns = [col for col in total_data.columns if col not in [factor_name]]
    ind_styles = industry_styles if is_ind_neutralize else []
    custom_risk_styles = [i for i in custom_risk_styles.split(',') if len(i) > 2] if len(custom_risk_styles) > 0 else []
    neutralized_styles = ind_styles + custom_risk_styles
    for k, g in grouped:
        if len(g) < 2:
            continue
        new_factors = factor_processing(g[[factor_name]].values,
                 pre_process=[winsorize_normal,standardize] if pre_process else None,
                 risk_factors=g[neutralized_styles].values.astype(float) if len(neutralized_styles) > 0 else None,
                 post_process=[winsorize_normal,standardize] if post_process else None)
        f = pd.DataFrame(new_factors, columns=[factor_name])
        for k in ndiff_columns:
            f[k] = g[k].values
        alpha_res.append(f)
    return pd.concat(alpha_res) if alpha_res else pd.DataFrame(columns=['trade_date',factor_name])