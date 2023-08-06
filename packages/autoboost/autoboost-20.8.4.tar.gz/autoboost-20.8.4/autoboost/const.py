"""Define the standard optimization dictionary for the boosting algorithms."""
from sklearn.metrics import get_scorer

UNIVERSAL_PARAMS_DEFAULT = [
    # set 1
    {'n_estimators': [30, 70, 100, 200, 300]},
    # set 2
    {'max_depth': [3, 5, 7, 9],
     'min_child_weight': [0.001, 0.1, 1, 5, 10, 20],
     'min_samples_split': [1, 2, 5, 10, 20, 30],
     'num_leaves': [15, 35, 50, 75, 100, 150]},
    # set 3
    {'gamma': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
     'min_samples_leaf': [1, 2, 5, 10, 20, 30],
     'min_child_samples': [2, 7, 15, 25, 45],
     'min_split_gain': [0, 0.001, 0.1, 1, 5, 20]},
    # set 4
    {'n_estimators': [30, 50, 70, 100, 150, 200, 300],
     'max_features': range(10, 25, 3)},
    # set 5
    {'subsample': [i / 10 for i in range(4, 10)],
     'colsample_bytree': [i / 10 for i in range(4, 10)],
     'feature_fraction': [i / 10 for i in range(4, 10)]},
    # set 6
    {'reg_alpha': [1e-5, 1e-2, 0.1, 1, 25, 100],
     'reg_lambda': [1e-5, 1e-2, 0.1, 1, 25, 100]}]

UNIVERSAL_PARAMS_SMALL = [
    # set 1
    {'n_estimators': [30, 50, 70]},
    # set 2
    {'learning_rate': [0.03, 0.3]},
    # set 3
    {'max_depth': [3, 5, 9],
     'min_child_weight': [0.001, 1, 20],
     'min_samples_split': [1, 2, 5, ],
     'num_leaves': [15, 35, 50]},
    # set 4
    {'gamma': [0.0, 0.2, 0.4, 0.5],
     'min_samples_leaf': [1, 2, 5],
     'min_child_samples': [2, 15, 45],
     'min_split_gain': [0, 0.1, 20]},
    # set 5
    {'n_estimators': [50, 200, 300], 'max_features': range(10, 21, 3)},
    # set 6
    {'subsample': [i / 10 for i in range(4, 8)],
     'colsample_bytree': [i / 10 for i in range(4, 8)],
     'feature_fraction': [i / 10 for i in range(4, 8)]},
    {'reg_alpha': [1e-5, 0.1, 1],
     'reg_lambda': [1e-5, 1, 100]}]


def get_mse():
    """Retrieve a valid scorer for mean squared error metric."""
    return get_scorer("neg_mean_squared_error")


def get_rmse():
    """Retrieve a valid scorer for mean squared error metric."""
    return get_scorer("neg_root_mean_squared_error")
