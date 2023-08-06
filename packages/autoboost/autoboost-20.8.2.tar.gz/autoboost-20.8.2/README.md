
![release](https://img.shields.io/github/v/release/gieses/autoboost)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Twitter](https://flat.badgen.net/twitter/follow/SvenHGiese?icon=twitter)](https://twitter.com/SvenHGiese/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
![PyPI version](https://img.shields.io/pypi/v/autoboost)
![coverage](.github/imgs/coverage.svg)

## autoboost

Automatic step-wise parameter optimization for xgboost, lightgbm and sklearn's GradingBoosting.

### Implemented Strategy

The optimization strategy is taken
from [SylwiaOliwia](https://github.com/SylwiaOliwia2/xgboost-AutoTune#xgboost-autotune).
We only incorporate slight changes to the implementation, e.g. we base all decision on the cross-validation
test folds and not the entire data set.

The following excerpt is also taken from the readme:

### General note

Full GridSearch is time- and memory-demanding, so xgboost-AutoTune tunes parameters in the following steps (one by one,
from the most robust to the less):

1. n_estimators
2. max_depth, min_child_weight
3. Gamma
4. n_estimators
5. Subsample, colsample_bytree
6. reg_alpha, reg_lambda
7. n_estimators and learning_rate

8. Some of them are related only to `xgboost`, `LightGBM` or `GBM`. Algorithm picks parameters valid for given model and
   skip the rest.

Model is updated by newly chosen parameters in each step.

#### Detailed notes

Algorithm make GridsearchCV for each in seven steps (see **General note** section) and choose the best value. It uses
domian values:

```python
{'n_estimators': [30, 50, 70, 100, 150, 200, 300]},
{'max_depth': [3, 5, 7, 9], 'min_child_weight': [0.001, 0.1, 1, 5, 10, 20], 'min_samples_split': [1, 2, 5, 10, 20, 30],
 'num_leaves': [15, 35, 50, 75, 100, 150]},
{'gamma': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5], 'min_samples_leaf': [1, 2, 5, 10, 20, 30],
 'min_child_samples': [2, 7, 15, 25, 45], 'min_split_gain': [0, 0.001, 0.1, 1, 5, 20]},
{'n_estimators': [30, 50, 70, 100, 150, 200, 300], 'max_features': range(10, 25, 3)},
{'subsample': [i / 10 for i in range(4, 10)], 'colsample_bytree': [i / 10 for i in range(4, 10)],
 'feature_fraction': [i / 10 for i in range(4, 10)]},
{'reg_alpha': [1e-5, 1e-2, 0.1, 1, 25, 100], 'reg_lambda': [1e-5, 1e-2, 0.1, 1, 25, 100]}
```

Unless user will provide his own dictionary of values in **initial_params_dict**.

In each iteration, if chosing the best value from array has improved **scoring** by **min_loss**, algorithm continue
searching. It creates new array from the best value, and 2 values in the neighbourhood:

* If the best value in the previous array had neighbours, then new neighbours will be average between best value and
  it's previous neighbours. Example: if the best value from `n_estimators`: `[30, 50, 70, 100, 150, 200, 300]` will be
  70, than the new array to search will be `[60, 70, 85]`.

* If the best value is the lowest from the array, it's new value will be `2*best_value- following_value` unless it's
  bigger then minimal (otherwise minimal posible value).

* The the best value was the biggest in the array, it will be treated in the similar way, as the lowest one.

If new values are float and int is required, values are rounded.

`n_estimators` and `learning_rate` are chosen pairwise. Algorithm takes its values from model and train them pairwise: (
n* `n_estimators` , `learning_rate`/ n ).

### Installation

autoboost is available on PyPi and conda. You can easily install the package via:

```console
conda install -c conda-forge autoboost
```

or alternatively via pip:

```console
pip install autoboost
```

### Usage

The standard usage can be summarized as follows:

```python
from autoboost import optimizer

bo = optimizer.BoostingOptimizer(initial_model=xgboost.XGBRegressor(), scorer=mse_scorer)
clf = bo.fit(x_train, y_train)
```

Please the example file for a full working example for [regression](example/regression_diamonds.py)
and [classification](example/classification_iris.py).

## Sources

The following list of sources is taking from xgboost-AutoTune.

- autoboost is based on [xgboost-AutoTune](!https://github.com/SylwiaOliwia2/xgboost-AutoTune)
- https://xgboost.readthedocs.io/en/stable/tutorials/param_tuning.html
- https://www.analyticsvidhya.com/blog/2016/03/complete-guide-parameter-tuning-xgboost-with-codes-python/
- https://machinelearningmastery.com/tune-number-size-decision-trees-xgboost-python/
- https://www.kaggle.com/prasunmishra/parameter-tuning-for-xgboost-sklearn/notebook
- https://cambridgespark.com/content/tutorials/hyperparameter-tuning-in-xgboost/index.html 