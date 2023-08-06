import pandas as pd
import numpy as np


from sklearn.metrics import (
    recall_score,
    make_scorer,
    roc_auc_score,
    confusion_matrix,
)

from scipy import stats


def eval_information_value(column, target, y_values=[0, 1], goods=0, treat_inf=False):
    def check_value(x, ref):
        return np.sum(np.where(x == ref, 1, 0))

    data = pd.DataFrame({"feature": column, "target": target})

    df = data.groupby("feature").agg(
        **{
            "total": ("target", "count"),
        }
    )

    for val in y_values:

        df = df.merge(
            data.groupby("feature").agg(
                **{
                    str(val): ("target", lambda x: check_value(x, val)),
                }
            ),
            left_index=True,
            right_index=True,
            how="left",
        )

        sum_val = df[str(val)].sum()
        df["%" + str(val)] = df[str(val)] / sum_val

    def log_0(c_0, c_1):
        if c_0 == 0:
            return -np.inf
        elif c_1 == 0:
            return np.inf
        elif (c_0 != 0) & (c_1 != 0):
            return np.log(c_0 / c_1)

    if goods == 0:
        df["woe"] = df.apply(lambda row: log_0(row["%0"], row["%1"]), axis=1)
        df["iv"] = (df["%0"] - df["%1"]) * df["woe"]
    else:
        df["woe"] = df.apply(lambda row: log_0(row["%0"], row["%1"]), axis=1)
        df["iv"] = (df["%1"] - df["%0"]) * df["woe"]

    if treat_inf:
        df = treat_iv_infinity(df)

    return df


def treat_iv_infinity(iv_table):
    iv = iv_table.copy()
    iv.loc[np.abs(iv["woe"]) == np.inf, "iv"] = 0
    min_woe = iv[np.abs(iv["woe"]) != np.inf]["woe"].min()
    max_woe = iv[np.abs(iv["woe"]) != np.inf]["woe"].max()
    amp_woe = max_woe - min_woe
    iv.loc[iv["woe"] == np.inf, "woe"] = max_woe + 0.5 * amp_woe
    iv.loc[iv["woe"] == -np.inf, "woe"] = min_woe - 0.5 * amp_woe
    return iv


def roc_auc_scorer(y_true, y_pred):
    """Evaluates the area under the ROC curve"""
    return roc_auc_score(y_true, y_pred)


def ks_2sample(y, y_prob):
    """Evaluates the KS statistics"""
    df = pd.DataFrame({"prob": y_prob, "y": y})
    dist_bad = df.loc[df["y"] == 1, "prob"]
    dist_good = df.loc[df["y"] == 0, "prob"]
    return stats.ks_2samp(dist_bad, dist_good)[0]


def ks_auc_scorer(y_true, y_prob):
    """Evaluates the area under the ROC curve"""
    auc = roc_auc_scorer(y_true, y_prob) / 0.91
    ks = ks_2sample(y_true, y_prob) / 0.70

    return auc * ks / (auc + ks)


def tnr_score(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return tn / (tn + fp)


def tnr_tpr_mean(y_true, y_pred):
    tnr = tnr_score(y_true, y_pred)
    tpr = recall_score(y_true, y_pred)
    return 0.6 * tnr + 0.4 * tpr

# tnr_tpr_mean_score = make_scorer(tnr_tpr_mean, greater_is_better=True)
# auc_score = make_scorer(roc_auc_scorer, needs_proba=True, greater_is_better=True)
# ks_score = make_scorer(ks_2sample, needs_proba=True, greater_is_better=True)
# ks_auc_score = make_scorer(ks_auc_scorer, needs_proba=True, greater_is_better=True)
