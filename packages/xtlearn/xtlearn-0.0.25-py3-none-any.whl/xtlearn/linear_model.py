import pandas as pd
import numpy as np
from sklearn import linear_model


class LogisticRegression(linear_model.LogisticRegression):
    def __init__(
        self,
        penalty="l2",
        *,
        dual=False,
        tol=0.0001,
        C=1.0,
        fit_intercept=True,
        intercept_scaling=1,
        class_weight=None,
        random_state=None,
        solver="lbfgs",
        max_iter=100,
        multi_class="auto",
        verbose=0,
        warm_start=False,
        n_jobs=None,
        l1_ratio=None,
    ):
        super().__init__(
            penalty=penalty,
            dual=dual,
            tol=tol,
            C=C,
            fit_intercept=fit_intercept,
            intercept_scaling=intercept_scaling,
            class_weight=class_weight,
            random_state=random_state,
            solver=solver,
            max_iter=max_iter,
            multi_class=multi_class,
            verbose=verbose,
            warm_start=warm_start,
            n_jobs=n_jobs,
            l1_ratio=l1_ratio,
        )

    def transform(self, X):
        return X

    def predict(self, X, threshold=0.5):
        return _threshold_predict(super(), X, threshold=threshold)


def _threshold_predict(model, X, threshold=0.5):
    predict_prob = model.predict_proba(X)[:, 1]

    return _predict_from_prob(predict_prob, threshold)


def _predict_from_prob(y_prob, threshold):
    condition = lambda x: x > threshold
    vec_condition = np.vectorize(condition)
    return np.where(vec_condition(y_prob), 1.0, 0.0)
