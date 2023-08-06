"""
Optimizer for Gradient Boosting Machines (XGBoost, sklearn, lightgbm).

This implementation is mostly taken from Sylwia Oliwia's GitHub. Please visit the original repository for the
original implementation https://github.com/SylwiaOliwia2/xgboost-AutoTune.
"""
from typing import Any, Optional, Union, Literal

import lightgbm
import numpy as np
import pandas as pd
import xgboost
from sklearn import ensemble
from sklearn.model_selection import GridSearchCV
from tqdm import tqdm

from autoboost.const import UNIVERSAL_PARAMS_DEFAULT, UNIVERSAL_PARAMS_SMALL, get_mse

_DICT_NAMES = Literal["small", "default"]


class BoostingOptimizer:
    """
    Boosting Optimizer for step-wise parameter optimization of Gradient Boosting Classifiers.

    Attributes:
        initial_model: Any, boosting classifier
        initial_param_dic: dict, parameter dict to start with
        available_params: list, defines the allowed parameters for the classifier
        best_params: dict, will store the best parameters.

    Retrieve the valid models via:
    >>>BoostingOptimizer.print_valid_models()
    """

    _MODELS = ['XGBRegressor', 'GradientBoostingRegressor', 'LGBMRegressor',
               "XGBClassifier", "GradientBoostingClassifier", "LGBMClassifier"]
    _MODEL_CLASSES = [xgboost.XGBRegressor, ensemble.GradientBoostingRegressor, lightgbm.LGBMRegressor,
                      xgboost.XGBClassifier, ensemble.GradientBoostingClassifier, lightgbm.LGBMClassifier]

    @staticmethod
    def print_valid_models() -> None:
        """Print the valid models."""
        print(BoostingOptimizer._MODELS)

    def __init__(self,
                 initial_model: Optional[Any] = xgboost.XGBRegressor(),
                 scorer: Optional[Any] = None,
                 initial_params_dict: Optional[Union[_DICT_NAMES, dict]] = None,
                 min_loss: float = 0.1,
                 n_folds: int = 5,
                 n_jobs: int = -1,
                 n_jobs_grid: int = 1,
                 verbose: int = 0,
                 factors: list[int] = None,
                 seed: int = 2022):
        """
        Optimizer for gradient boosting.

        Example:
        >>> bo = BoostingOptimizer()
        >>> bo.fit(x, y)

        Parameters
        ----------
        initial_model: Any,
            Gradient Boosting Object to optimize. (default: xgboost regressor)
        scorer: Any,
            sklearn's scorer object that is used during grid search. (default: negative mse)
        initial_params_dict: str or dict,
            if provided overwrites the autoboost dict for optimization.
        min_loss: float,
            minimal loss that needs to be met to stop optimization / extension of parameters.
        n_folds: int,
            number of cross-validation folds.
        n_jobs: int,
            n_jobs to runi n parallel (supplied to gradient boosting machine)
        n_jobs_grid: int,
            n:jobs to run in parallel (supplied to gridsearch)
        factors: list[int],
            after the initial parameter sweeps, a final combined sweep of increasing number of treas and decreasing
            learning rate is done. The factors define the size of this list. For example, if the best found hyper-
            parameter for number of trees was 10 and factors is [5, 10], the grid search is again performed with
            50 and 100 trees (similarly with the learning rate).
        verbose: int,
            verbosity of the optimization (disable to -1).
        """
        # check if input is supported
        if not initial_params_dict:
            initial_params_dict = UNIVERSAL_PARAMS_DEFAULT

        elif isinstance(initial_params_dict, str):
            if initial_params_dict == "small":
                initial_params_dict = UNIVERSAL_PARAMS_SMALL
            elif initial_params_dict == "default":
                initial_params_dict = UNIVERSAL_PARAMS_DEFAULT
            else:
                raise ValueError(
                    f"Provided parameters not supported ({initial_params_dict}), must be one of: {_DICT_NAMES}")

        if not scorer:
            scorer = get_mse()

        # set
        if (initial_model.__class__.__name__ not in BoostingOptimizer._MODELS):
            BoostingOptimizer.print_valid_models()
            raise AssertionError("Please provide a valid boosting model.")

        if min_loss == 0.0:
            raise AssertionError(f"min loss must be strictly different from zero. You provided: {min_loss}")
        if n_folds <= 1:
            raise AssertionError(f"n_folds must be greater than 1. You provided: {n_folds}")

        # model specifics
        self.initial_model = initial_model
        self.initial_param_dic = initial_params_dict
        self.available_params = list(initial_model.get_params().keys())
        self.best_params = initial_model.get_params()
        # FIXME: add random_sate, see for later xgboost release if it works.
        self.best_params.update({"random_state": seed, "n_jobs": n_jobs})

        # optimization parameters
        self.scorer = scorer
        self.min_loss = min_loss
        self.n_folds = n_folds
        self.seed = seed

        # processing parameters
        self.n_jobs = n_jobs
        self.n_jobs_grid = n_jobs_grid
        self.verbose = verbose

        self.cv_results = []
        self.model = None
        if isinstance(factors, np.ndarray):
            pass
        elif isinstance(factors, list):
            factors = np.array(factors)
        else:
            factors = np.array([1, 5, 10, 15])
        self.factors = factors

    def fit(self, X, y) -> Any:
        """
        Fit the Boosting Optimizer.

        Parameters
        ----------
        X: pd.DataFrame,
            training data, note that categorical variables need to be properly encoded
        y: pd.DataFrame or Series,
            training data labels / measurements

        Returns
        -------
        fitted model,
            the trained classifier model
        """
        # step-wise optimization
        for param_combi in tqdm(self.get_optimization_tasks(), desc="sweeping parameters:"):
            # get model
            if self.verbose:
                print("##########################################################")
                print(f"Sweeping: {param_combi}")
                print(f"Current Best Params: {self.best_params}")
            model = self.initial_model
            model.set_params(**self.best_params)
            if self.verbose:
                print(f"Current Model Params: {self.best_params}")

            # grid search
            gs = self.find_best_param(model, param_combi, X, y)
            best_combi_params = gs.best_params_
            self.best_params.update(best_combi_params)

        # final optimization
        if self.best_params['learning_rate'] is None:
            self.best_params['learning_rate'] = 0.3

        final_param_sweep = [{"n_estimators": [i], "learning_rate": [j]} for i, j in zip(
            self.best_params['n_estimators'] * self.factors,
            self.best_params['learning_rate'] / self.factors)]
        clf = GridSearchCV(model, final_param_sweep, scoring=self.scorer, verbose=self.verbose, cv=self.n_folds,
                           refit=True, n_jobs=self.n_jobs_grid)
        clf.fit(X, y)
        if self.verbose:
            print(f"final sweep best params: {clf.best_params_}")

        # final fit with early stopping
        return clf

    def find_best_param(self, model: Any, parameters: dict,
                        x_train: pd.DataFrame, y_train: pd.DataFrame,
                        initial_score: float = 0, trial: int = 0) -> GridSearchCV:
        """
        Find the best parameter for a limited set of hyper-parameter combinations.

        Parameters
        ----------
        model: any,
            a fresh model that is not fitted.
        parameters: dict,
            Parameters to optimize.
        x_train: pd.DataFrame,
            training data x
        y_train: pd.DataFrame,
            training labels, observations.
        initial_score: float,
            the initial score to further optimize
        trial: int,
            number of trials for extending a specific set of parameters

        Returns
        -------
        GridSearchCV,
            fitted GridSearchCV results.
        """
        param_requirments = {'subsample': {'max': 1, 'min': 1 / len(x_train), 'type': 'float'},
                             # minimal value is fraction for one row
                             'colsample_bytree': {'max': 1, 'min': 1 / len(x_train.columns), 'type': 'float'},
                             # # minimal value is fraction for one column
                             'reg_alpha': {'max': np.inf, 'min': 0, 'type': 'float'},
                             'reg_lambda': {'max': np.inf, 'min': 0, 'type': 'float'},
                             'reg_scale_pos_weightlambda': {'max': np.inf, 'min': 0, 'type': 'float'},
                             'learning_rate': {'max': 1, 'min': 1e-15, 'type': 'float'},
                             # technically it moght be more than 1, but it may lead to underfittting
                             'n_estimators': {'max': np.inf, 'min': 1, 'type': 'int'},
                             'max_features': {'max': np.inf, 'min': 1, 'type': 'int'},
                             'gamma': {'max': np.inf, 'min': 0, 'type': 'float'},
                             'min_samples_leaf': {'max': np.inf, 'min': 1, 'type': 'int'},
                             # could be float (then i'ts percentage of all examples, but we'll use integers
                             # (number of samples) for consistency)
                             'min_samples_split': {'max': np.inf, 'min': 2, 'type': 'int'},
                             # could be float (then i'ts percentage of all examples, but we'll use integers
                             # (number of samples) for consistency)
                             'min_child_samples': {'max': np.inf, 'min': 1, 'type': 'int'},
                             'min_split_gain': {'max': np.inf, 'min': 0, 'type': 'float'},
                             'min_child_weight': {'max': np.inf, 'min': 0, 'type': 'float'},
                             'max_depth': {'max': np.inf, 'min': 1, 'type': 'int'},
                             'num_leaves': {'max': np.inf, 'min': 2, 'type': 'int'}}

        if self.verbose:
            print(f"Find best parameters, Trial: #{trial}, Grid: ", parameters)
        clf = GridSearchCV(model, parameters, scoring=self.scorer, verbose=self.verbose, cv=self.n_folds, refit=True,
                           n_jobs=self.n_jobs_grid)
        clf.fit(x_train, y_train)

        # scoring fun for regression / classification tasks
        # this gives the right sign for optimization
        # new_score_exp = self.scorer._score_func(clf.predict(x_train), y_train)
        new_score = self.scorer._sign * self.scorer(clf.best_estimator_, x_train, y_train)

        # store meta information
        gs_results_df = pd.DataFrame(clf.cv_results_)
        gs_results_df["paramter_grid"] = str(parameters)
        gs_results_df["parameter_best"] = str(clf.best_params_)
        gs_results_df["score_initial"] = initial_score
        gs_results_df["score_current"] = new_score
        self.cv_results.append(gs_results_df.round(3))
        if self.verbose:
            print(f"Best Estimator: {clf.best_params_}")

        # stopping criteria met?
        if (new_score - initial_score) > self.min_loss:
            new_param_dict = {}
            for param_name, param_array in parameters.items():
                if len(param_array) > 1:
                    # get best parameter and adjust new grid based on the best parameter
                    position = param_array.index(clf.best_params_[param_name])
                    adj_param_grid = self.define_new_param_borders(param_name, param_array, position,
                                                                   param_requirments)
                    # assign new array if it's different than the old one
                    if (len(adj_param_grid) != len(param_array)) or (adj_param_grid != param_array).any():
                        new_param_dict[param_name] = list(adj_param_grid)

            # recursive fun part
            if len(new_param_dict) > 0:
                self.find_best_param(model, new_param_dict, x_train, y_train, initial_score=new_score,
                                     trial=trial + 1)
        return clf

    def get_optimization_tasks(self) -> list[dict]:
        """
        Generate a list of parameter combinations that are valid with respect to the model.

        Returns
        -------
            valid_grid: iterable,
                each entry in the list will be a valid dictionary for the classifier.
        """
        valid_params = set(self.available_params)

        valid_grid = []
        for param_step_grid in self.initial_param_dic:
            # only append parameters that are supported by the model
            valid_keys = [i for i in param_step_grid.keys() if i in valid_params]
            valid_grid.append({k: param_step_grid[k] for k in valid_keys})
        return valid_grid

    @staticmethod
    def define_new_param_borders(param_name: str, param_values: list, best_index: int, param_requirements: dict):
        """
        Define new parameters to be swept based on the best prior result.

        The strategy extends / narrows the last grid of a hyper-parameter to an array of three values.

        Parameters
        ----------
        param_name: str,
            name of the parameter
        param_values: list,
            values of that parameter ('grid')
        best_index: int,
            the best performing previous value.
        param_requirements: dict,
            dictionary, with valid ranges for hyper-parameters.

        Returns
        -------
            new_grid: list,
                new hyper-parameter grid to be searched

        Example
        -------
        >>> valid_range = {"n_estimators": {'max': np.inf, 'min': 1, 'type': 'int'}}
        >>> define_new_param_borders("n_estimators", [30, 50, 70], 1, valid_range)
         array([40, 50, 60])
        """
        # best parameter was at position 0
        if best_index == 0:
            lowest_val = param_values[best_index] * 2 - param_values[best_index + 1]
            highest_val = (param_values[best_index + 1] + param_values[best_index]) / 2

        # best parameter was at last position
        elif param_values[-1] == param_values[best_index]:
            lowest_val = ((param_values[best_index - 1] + param_values[best_index]) / 2)
            highest_val = ((param_values[best_index] * 2 + param_values[best_index - 1]) / 2)

        # best parameter was in the middle
        else:
            lowest_val = (param_values[best_index - 1] + param_values[best_index]) / 2
            highest_val = (param_values[best_index + 1] + param_values[best_index]) / 2

        # check validity of values
        if lowest_val < param_requirements[param_name]['min']:
            lowest_val = param_requirements[param_name]['min']
        if highest_val > param_requirements[param_name]['max']:
            highest_val = param_requirements[param_name]['max']

        new_param_grid = np.array([lowest_val, param_values[best_index], highest_val])

        # check data type requirements
        if param_requirements[param_name]['type'] == 'int':
            new_param_grid[0] = np.ceil(new_param_grid[0])
            new_param_grid[-1] = np.floor(new_param_grid[-1])
            new_param_grid[1:-1] = np.round(new_param_grid[1:-1])
            new_param_grid = new_param_grid.astype(int)

        return np.unique(new_param_grid)
