import pandas as pd
import numpy as np
from tqdm import tqdm
import random
from sklearn.model_selection import cross_validate


class MetropolisHastingSearch:
    def __init__(
        self,
        estimator,
        param_distributions,
        first_guess,
        n_iter=10,
        scoring=None,
        cv=None,
        verbose=0,
        random_state=None,
    ):

        self.estimator = estimator
        self.param_distributions = param_distributions
        self.first_guess = first_guess
        self.n_iter = n_iter
        self.scoring = scoring
        self.cv = cv
        self.random_state = random_state
        self.verbose = verbose
        self.__current_param = self.first_guess
        self.max_param = None
        self.max_score = None

    def new_param(self, input_param):

        result = {}
        for par in self.param_distributions:
            result[par] = np.random.choice(self.param_distributions[par])

        return result

    def scoring_function(self, X, y, param):
        new_estimator = self.estimator.__class__(**param)

        results = self.eval_score(X=X, estimator=new_estimator, y=y)

        return np.log(results["test_score"].mean())

    def eval_score(self, X, estimator, y=None):

        results = cross_validate(
            estimator,
            X,
            y,
            scoring=self.scoring,
            cv=self.cv,
        )

        return results

    def fit(self, X, y):
        log_p = self.scoring_function(X, y, self.__current_param)

        # print('max_param:',self.__current_param,' | ',np.exp(log_p))

        if self.max_score is not None:
            if np.exp(log_p) > self.max_score:
                self.max_score = np.exp(log_p)
                self.max_param = self.__current_param
        else:
            self.max_score = np.exp(log_p)
            self.max_param = self.__current_param

        par_list = []

        for i in tqdm(range(self.n_iter)):

            par_0 = self.new_param(self.__current_param)
            log_p0 = self.scoring_function(X, y, par_0)

            if log_p0 > log_p:
                self.__current_param = par_0
                log_p = log_p0

            if log_p0 > np.log(self.max_score):
                self.max_score = np.exp(log_p0)
                self.max_param = par_0

            else:
                u = random.uniform(0.0, 1.0)
                if u < np.exp(log_p0 - log_p):
                    self.__current_param = par_0
                    log_p = log_p0

            par_list.append(
                {"n": i, "prob": np.exp(log_p), "params": self.__current_param}
            )

        self.__current_param = self.max_param

        return {
            "max_param": self.max_param,
            "max_score": self.max_score,
            "param_list": par_list,
        }
