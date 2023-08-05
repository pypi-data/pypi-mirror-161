import pandas as pd
import pdb
from sklearn.model_selection import KFold
from ultron.optimize.model.modelbase import load_module


def model_fitness(features, model_name, X, Y, params, mode, n_splits):
    kf = KFold(n_splits=n_splits, shuffle=False)
    res = []
    for train_index, test_index in kf.split(X):
        x_train = X.iloc[train_index]
        y_train = Y.iloc[train_index].values
        x_test = X.iloc[test_index]
        y_test = Y.iloc[test_index].values
        model = load_module(model_name)(features=features, **params)
        model.fit(x_train, y_train)
        res.append({
            'score': model.score(x_test, y_test),
            'accuracy': model.accuracy(x_test, y_test),
            'precision': model.precision(x_test, y_test),
            'recall': model.recall(x_test, y_test)
        })
    result = pd.DataFrame(res)
    mode_name = mode if mode in result.columns else 'accuracy'
    return 0 if result.empty else result[mode_name].mean()