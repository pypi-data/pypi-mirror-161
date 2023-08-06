#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Description
----------
Some simple classes to be used in sklearn pipelines for pandas input

Informations
----------
    Author: Eduardo M.  de Morais
    Maintainer:
    Email: emdemor415@gmail.com
    Copyright:
    Credits:
    License:
    Version:
    Status: in development
    
"""
import numpy, math, scipy, pandas
import numpy as np
import pandas as pd
from scipy.stats import zscore


from sklearn.base import BaseEstimator, TransformerMixin

# from IPython.display import clear_output
from sklearn import preprocessing
from sklearn.preprocessing import (
    # MinMaxScaler,
    RobustScaler,
    KBinsDiscretizer,
    KernelCenterer,
    QuantileTransformer,
)
from sklearn.pipeline import Pipeline

from scipy import stats

from .metrics import eval_information_value


class ReplaceValue(BaseEstimator, TransformerMixin):
    """
    Description
    ----------
    Replace all values of a column by a specific value.

    Arguments
    ----------
    feature_name: str
        name of the column to replace

    value:
        Value to be replaced

    replace_by:
        Value to replace

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        in the final score

    Examples
    ----------
        >>> replace = ReplaceValue('first_col','val','new_val')
        >>> replace.fit_transform(X,y)
    """

    def __init__(self, feature_name, value, replace_by, active=True):
        self.active = active
        self.feature_name = feature_name
        self.value = value
        self.replace_by = replace_by

    def fit(self, X, y):
        return self

    def transform(self, X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def __transformation(self, X_in):
        X = X_in.copy()
        X[self.feature_name] = X[self.feature_name].replace(self.value, self.replace_by)
        return X


class OneFeatureApply(BaseEstimator, TransformerMixin):
    """
    Description
    ----------
    Apply a passed function to all elements of column

    Arguments
    ----------
    feature_name: str
        name of the column to replace

    apply: str
        String containing the lambda function to be applied

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        in the final score

    Examples
    ----------
        >>> apply = OneFeatureApply(feature_name = 'first_col',apply = 'np.log1p(x/2)')
        >>> apply.fit_transform(X_trn,y_trn)
    """

    def __init__(self, feature_name, apply="x", active=True, variable="x"):
        self.feature_name = feature_name
        self.apply = eval("lambda ?: ".replace("?", variable) + apply)
        self.active = active

    def fit(self, X, y):
        return self

    def transform(self, X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def __transformation(self, X_in):
        X = X_in.copy()
        X[self.feature_name] = self.apply(X[self.feature_name])
        return X


class FeatureApply(BaseEstimator, TransformerMixin):
    """
    Description
    ----------
    Apply a multidimensional function to the features.

    Arguments
    ----------

    apply: str
        String containing a multidimensional lambda function to be applied. The name of the columns must appear in the string inside the tag <>. Ex. `apply = "np.log(<column_1> + <column_2>)" `

    destination: str
        Name of the column to receive the result

    drop: bool
        The user choose if the old features columns must be deleted.

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        in the final score

    Examples
    ----------
        >>> apply = FeatureApply( destination = 'result_column', apply = 'np.log1p(<col_1> + <col_2>)')
        >>> apply.fit_transform(X_trn,y_trn)

    """

    def __init__(self, apply="x", active=True, destination=None, drop=False):
        self.apply = apply
        self.active = active
        self.destination = destination
        self.drop = drop

    def fit(self, X, y):
        return self

    def transform(self, X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def __transformation(self, X_in):
        X = X_in.copy()

        cols = list(X.columns)
        variables = self.__get_variables(self.apply, cols)
        len_variables = len(variables)

        new_column = self.__new_column(self.apply, X)

        if self.drop:
            X = X.drop(columns=variables)

        if self.destination:
            if self.destination == "first":
                X[variables[0]] = new_column

            elif self.destination == "last":
                X[variables[-1]] = new_column

            else:
                if type(self.destination) == str:
                    X[self.destination] = new_column
                else:
                    print(
                        '[Warning]: <destination> is not a string. Result is on "new_column"'
                    )
                    X["new_column"] = new_column
        else:
            if len_variables == 1:
                X[variables[0]] = new_column
            else:
                X["new_column"] = new_column

        return X

    def __findall(self, string, pattern):
        return [i for i in range(len(string)) if string.startswith(pattern, i)]

    def __remove_duplicates(self, x):
        return list(dict.fromkeys(x))

    def __get_variables(self, string, checklist, verbose=1):

        start_pos = self.__findall(string, "<")
        end_pos = self.__findall(string, ">")

        prop_variables = self.__remove_duplicates(
            [string[start + 1 : stop] for start, stop in zip(start_pos, end_pos)]
        )

        variables = []

        for var in prop_variables:
            if var in checklist:
                variables.append(var)
            else:
                if verbose > 0:
                    print("[Error]: Feature " + var + " not found.")

        return variables

    def __new_column(self, string, dataframe):
        cols = list(dataframe.columns)
        variables = self.__get_variables(string, cols, verbose=0)
        function = eval(
            "lambda "
            + ",".join(variables)
            + ": "
            + string.replace("<", "").replace(">", "")
        )

        new_list = []
        for ind, row in dataframe.iterrows():
            if len(variables) == 1:
                var = eval("[row['" + variables[0] + "']]")
            else:
                var = eval(
                    ",".join(list(map(lambda st: "row['" + st + "']", variables)))
                )

            new_list.append(function(*var))

        return new_list


class Encoder(BaseEstimator, TransformerMixin):
    """
    Description
    ----------
    Encodes categorical features

    Arguments
    ----------

    drop_first: boll
        Whether to get k-1 dummies out of k categorical levels by removing the first level.

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        in the final score

    """

    def __init__(self, active=True, drop_first=True):
        self.active = active
        self.drop_first = drop_first

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def __transformation(self, X_in):
        return pd.get_dummies(X_in, drop_first=self.drop_first)


class OneHotMissingEncoder(BaseEstimator, TransformerMixin):
    """ """

    def __init__(self, columns, suffix="nan", sep="_", dummy_na=True, drop_last=False):
        """ """
        self.columns = columns
        self.suffix = suffix
        self.sep = sep

        self.any_missing = None
        self.column_values = None
        self.last_value = None

        self.dummy_na = dummy_na
        self.drop_last = drop_last

    def transform(self, X, **transform_params):
        """ """
        X_copy = X.copy()

        final_columns = []

        for col in X_copy.columns:
            if col not in self.columns:
                final_columns.append(col)
            else:
                for value in self.column_values[col]:
                    col_name = col + self.sep + str(value)
                    if (
                        self.drop_last
                        and value == self.last_value[col]
                        and (not self.any_missing[col])
                    ):
                        pass  # dropping

                    else:
                        final_columns.append(col_name)
                        X_copy[col_name] = (X_copy[col] == value).astype(int)

                if self.any_missing[col]:
                    if self.dummy_na and not self.drop_last:
                        col_name = col + self.sep + "nan"
                        final_columns.append(col_name)
                        X_copy[col_name] = pd.isnull(X_copy[col]).astype(int)

        return X_copy[final_columns]

    def fit(self, X, y=None, **fit_params):
        """ """
        self.any_missing = {col: (pd.notnull(X[col]).sum() > 0) for col in self.columns}

        self.column_values = {
            col: sorted([x for x in list(X[col].unique()) if pd.notnull(x)])
            for col in self.columns
        }

        self.last_value = {col: self.column_values[col][-1] for col in self.columns}

        return self


class MeanModeImputer(BaseEstimator, TransformerMixin):
    """

    Description
    ----------
    Not documented yet

    Arguments
    ----------
    Not documented yet

    """

    def __init__(self, features="all", active=True):
        self.features = features
        self.active = active

    def fit(self, X, y=None):

        if self.features == "all":
            self.features = list(X.columns)

        # receive X and collect its columns
        self.columns = list(X.columns)

        # defining the categorical columns of X
        self.numerical_features = list(X._get_numeric_data().columns)

        # definig numerical columns of x
        self.categorical_features = list(
            set(list(X.columns)) - set(list(X._get_numeric_data().columns))
        )

        self.mean_dict = {}

        for feature_name in self.features:
            if feature_name in self.numerical_features:
                self.mean_dict[feature_name] = X[feature_name].mean()
            elif feature_name in self.categorical_features:
                self.mean_dict[feature_name] = X[feature_name].mode()[0]

        return self

    def transform(self, X, y=None):
        if not self.active:
            return X
        else:
            return self.__transformation(X, y)

    def __transformation(self, X_in, y_in=None):
        X = X_in.copy()

        for feature_name in self.features:

            new_list = []

            if X[feature_name].isna().sum() > 0:
                for ind, row in X[[feature_name]].iterrows():
                    if pd.isnull(row[feature_name]):
                        new_list.append(self.mean_dict[feature_name])
                    else:
                        new_list.append(row[feature_name])

                X[feature_name] = new_list
        return X


class ScalerDF(BaseEstimator, TransformerMixin):
    """"""

    def __init__(self, max_missing=0.0, active=True):
        self.active = active
        self.max_missing = max_missing

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def __transformation(self, X_in):
        X = X_in.copy()
        scaler = preprocessing.MinMaxScaler(copy=True, feature_range=(0, 1))

        try:
            ind = np.array(list(X.index)).reshape(-1, 1)
            ind_name = X.index.name

            df = pd.concat(
                [
                    pd.DataFrame(scaler.fit_transform(X), columns=list(X.columns)),
                    pd.DataFrame(ind, columns=[ind_name]),
                ],
                1,
            )

            X = df.set_index("Id")

        except:
            X = pd.DataFrame(scaler.fit_transform(X), columns=list(X.columns))

        return X


def _dataframe_transform(transformer, data):
    if isinstance(data, (pd.DataFrame)):
        return pd.DataFrame(
            transformer.transform(data), columns=data.columns, index=data.index
        )
    else:
        return transformer.transform(data)


class MinMaxScaler(preprocessing.MinMaxScaler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def transform(self, X):
        return _dataframe_transform(super(), X)


class StandardScaler(preprocessing.StandardScaler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def transform(self, X):
        return _dataframe_transform(super(), X)


class RobustScaler(preprocessing.RobustScaler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def transform(self, X):
        return _dataframe_transform(super(), X)


class DataFrameImputer(TransformerMixin):
    def __init__(self):
        """
        https://stackoverflow.com/a/25562948/14204691

        Impute missing values.

        Columns of dtype object are imputed with the most frequent value
        in column.

        Columns of other types are imputed with mean of column.

        """

    def fit(self, X, y=None):

        self.fill = pd.Series(
            [
                X[c].value_counts().index[0]
                if X[c].dtype == np.dtype("O")
                else X[c].mean()
                for c in X
            ],
            index=X.columns,
        )

        return self

    def transform(self, X, y=None):
        return X.fillna(self.fill)


class EncoderDataframe(TransformerMixin):
    """"""

    def __init__(self, separator="_", drop_first=True):
        self.numerical_features = None
        self.categorical_features = None
        self.separator = separator
        self.drop_first = drop_first

        #

    def fit(self, X, y=None):

        # receive X and collect its columns
        self.columns = list(X.columns)

        # defining the categorical columns of X
        self.numerical_features = list(X._get_numeric_data().columns)

        # definig numerical columns of x
        self.categorical_features = list(
            set(list(X.columns)) - set(list(X._get_numeric_data().columns))
        )

        # make the loop through the columns
        new_columns = {}

        for col in self.columns:

            # if the column is numerica, append to new_columns
            if col in self.numerical_features:
                new_columns[col] = [col]

            # if it is categorical,
            elif col in self.categorical_features:

                # get all possible categories
                unique_elements = X[col].unique().tolist()

                # drop the last if the user ask for it
                if self.drop_first:
                    unique_elements.pop(-1)

                # make a loop through the categories
                new_list = []
                for elem in unique_elements:
                    new_list.append(elem)

                new_columns[col] = new_list

        self.new_columns = new_columns

        return self

    def transform(self, X, y=None):
        X_ = X.reset_index(drop=True).copy()

        # columns to be transformed
        columns = X_.columns

        # columns fitted
        if list(columns) != self.columns:
            print(
                "[Error]: The features in fitted dataset are not equal to the dataset in transform."
            )

        list_df = []
        for col in X_.columns:
            if col in self.numerical_features:
                list_df.append(X_[col])
            elif col in self.categorical_features:
                for elem in self.new_columns[col]:
                    serie = pd.Series(
                        list(map(lambda x: int(x), list(X_[col] == elem))),
                        name=str(col) + self.separator + str(elem),
                    )
                    list_df.append(serie)

        return pd.concat(list_df, 1)


from sklearn.preprocessing import OrdinalEncoder


class NumericBinner(BaseEstimator, TransformerMixin):
    """ """

    def __init__(self, columns=None, min_bins=None, max_bins=None, n_bins=None):

        """ """
        self.columns = columns
        self.binner = None
        self.bins = None
        self.min_bins = min_bins
        self.max_bins = max_bins
        self.n_bins = n_bins

        if (self.min_bins is None) and (self.max_bins is None) and (n_bins is None):
            self.min_bins = 2
            self.max_bins = 8

        elif (
            (self.min_bins is None) and (self.max_bins is None) and (n_bins is not None)
        ):
            self.min_bins = self.n_bins
            self.max_bins = self.n_bins

        elif (self.min_bins is None) and (self.max_bins is not None):
            self.min_bins = 2

        elif (self.min_bins is not None) and (self.max_bins is None):
            self.max_bins = 8

    def transform(self, X, **transform_params):
        """ """
        X_copy = X.copy()
        for column_name in self.columns:

            X_temp = X_copy.loc[X_copy[column_name].notna()][[column_name]].copy()

            X_temp = self.binner[column_name].transform(X_temp)

            X_copy.loc[X_copy[column_name].notna(), column_name] = X_temp.flatten() + 1

            X_copy.loc[X_copy[column_name].isna(), column_name] = 0

            X_copy[column_name] = X_copy[column_name].astype(int, errors="ignore")

            X_copy[column_name] = X_copy[column_name].apply(
                lambda x: self.bins[column_name]["woe"][x]
            )

        return X_copy

    def fit(self, X, y, **fit_params):
        """ """

        X_copy = X.copy()

        self.binner = {}
        self.bins = {}

        if self.columns is None:
            self.columns = X_copy.columns

        for column_name in self.columns:
            iv_temp = 0
            bin_temp = None
            binner_temp = None
            for i in range(2, self.max_bins + 1):
                X_local = X_copy.copy()

                X_temp = X_local.loc[X_local[column_name].notna()][[column_name]].copy()
                n = len(X_temp)

                n_unique = len(X_temp[column_name].unique())

                if n_unique >= i:

                    n_quant = 1000 if n >= 1000 else n

                    binner = Pipeline(
                        steps=(
                            ("scaler", RobustScaler()),
                            (
                                "quantile",
                                QuantileTransformer(
                                    output_distribution="uniform", n_quantiles=n_quant
                                ),
                            ),
                            (
                                "binning",
                                KBinsDiscretizer(
                                    n_bins=i, strategy="kmeans", encode="ordinal"
                                ),
                            ),
                        )
                    )

                    X_temp[column_name + "_transf"] = (
                        binner.fit_transform(X_temp).flatten() + 1
                    )
                    X_temp[column_name + "_transf"] = X_temp[
                        column_name + "_transf"
                    ].astype(int, errors="ignore")
                    X_temp.loc[X_copy[column_name].isna(), column_name + "_transf"] = 0

                    summary = X_temp.groupby(column_name + "_transf").agg(
                        min=(column_name, "min"),
                        max=(column_name, "max"),
                        mean=(column_name, "mean"),
                        std=(column_name, "std"),
                    )

                    X_local.loc[X_local[column_name].notna(), column_name] = X_temp[
                        column_name + "_transf"
                    ]

                    X_local.loc[X_copy[column_name].isna(), column_name] = 0
                    X_local[column_name] = X_local[column_name].astype(
                        int, errors="ignore"
                    )

                    iv = eval_information_value(
                        X_local[column_name],
                        y,
                        y_values=[0, 1],
                        goods=0,
                        treat_inf=True,
                    )

                    iv = iv.merge(
                        summary.reset_index(),
                        how="left",
                        right_on=column_name + "_transf",
                        left_index=True,
                    ).set_index(column_name + "_transf")

                    X_local[column_name] = X_local[column_name].apply(
                        lambda x: iv["woe"][x]
                    )

                    if (iv["iv"].sum() > iv_temp) & (
                        np.isfinite(X_local[column_name].unique()).all()
                    ):
                        iv_temp = iv["iv"].sum()
                        bin_temp = iv
                        bin_temp.index.name = "bin"
                        bin_temp = bin_temp.assign(total_iv=iv_temp)
                        binner_temp = binner

            self.bins[column_name] = bin_temp
            self.binner[column_name] = binner_temp

        return self

    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)


class KS2Selector(TransformerMixin):
    """ """

    def __init__(self, alpha=0.05, invalid_label="OTHER", features=None, min_count=10):
        self.invalid_label = invalid_label
        self.alpha = alpha
        self.features = features
        self.relevant_classes = None
        self.min_count = min_count

    def fit(self, X, y):

        classes_dict = {}
        for col in self.features:

            count_dict = X[col].value_counts().to_frame()

            class_1st = count_dict[count_dict[col] >= self.min_count].index

            list_ = []
            for class_ in class_1st:
                try:
                    ks_res = stats.ks_2samp(y[X[col] == class_], y[X[col] != class_])
                    list_.append((class_, *tuple(ks_res)))

                except:
                    pass

            df_temp = pd.DataFrame(list_, columns=[col, "KS", "pval"])

            relevant_classes = df_temp[df_temp["pval"] <= self.alpha][col]

            classes_dict[col] = list(relevant_classes)

        self.relevant_classes = classes_dict

        return self

    def transform(self, X, y=None):

        for col in self.relevant_classes:
            relevant_classes = self.relevant_classes[col]

            X[col] = np.where(
                np.isin(X[col], relevant_classes), X[col], self.invalid_label
            )

        return X

    def fit_transform(self, X, y):
        transformer = self.fit(X, y)
        return self.transform(X)


class Apply(BaseEstimator, TransformerMixin):
    def __init__(self, function, features="all", axis=0, active=True):
        self.features = features
        self.function = function
        self.axis = axis
        self.active = active

    def fit(self, X, y=None):
        if type(self.features) == str:
            if self.features == "all":
                if self.axis == 0:
                    self.features = list(X.columns)
            else:
                self.features = [self.features]

        return self

    def transform(self, X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def fit_transform(self, X, y=None, **fit_params):
        return super().fit_transform(X, y=y, **fit_params)

    def __transformation(self, X_in):
        X = X_in.copy()

        if type(self.features) == str:
            if self.features == "all":
                if self.axis == 1:
                    X = X.apply(self.function, axis=1)

        if (type(self.features) == list) or (type(self.features) == tuple):
            for col in self.features:
                X[col] = X[col].apply(self.function)

        return X


class FillNaWithColumn(BaseEstimator, TransformerMixin):
    def __init__(self, feature, column_source, active=True):
        self.feature = feature
        self.column_source = column_source
        self.active = active

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X[self.feature] = X[self.feature].fillna(X[self.column_source])
        return X

    def fit_transform(self, X, y=None, **fit_params):
        return super().fit_transform(X, y=y, **fit_params)


class FillNaWithValue(BaseEstimator, TransformerMixin):
    def __init__(self, feature, value, active=True):
        self.feature = feature
        self.value = value
        self.active = active

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X[self.feature] = X[self.feature].fillna(self.value)
        return X

    def fit_transform(self, X, y=None, **fit_params):
        return super().fit_transform(X, y=y, **fit_params)


class StringReplace(BaseEstimator, TransformerMixin):
    def __init__(self, features, pat, repl, n=-1, case=None, flags=0, regex=None):
        self.features = features
        self.pat = pat
        self.repl = repl
        self.n = n
        self.case = case
        self.flags = flags
        self.regex = regex

    def fit(self, X, y=None):
        if type(self.features) == str:
            self.features = [self.features]

        return self

    def transform(self, X):
        for col in self.features:
            X[col] = X[col].str.replace(
                pat=self.pat,
                repl=self.repl,
                n=self.n,
                case=self.case,
                flags=self.flags,
                regex=self.regex,
            )
        return X

    def fit_transform(self, X, y=None, **fit_params):
        return super().fit_transform(X, y=y, **fit_params)


class Converter(BaseEstimator, TransformerMixin):
    def __init__(self, features, type):
        self.features = features
        self.type = type

    def fit(self, X, y=None):
        if type(self.features) == str:
            self.features = [self.features]
        return self

    def transform(self, X):
        for col in self.features:
            X[col] = X[col].astype(self.type, errors="ignore")
        return X

    def fit_transform(self, X, y=None, **fit_params):
        return super().fit_transform(X, y=y, **fit_params)


class OutliersRemover(BaseEstimator, TransformerMixin):
    def __init__(self, features, z=3):
        self.features = features
        self.z = z

    def fit(self, X, y=None):
        if type(self.features) == str:
            self.features = [self.features]
        return self

    def transform(self, X):
        for col in self.features:
            X[col] = self.removing_outliers(X, col, z=self.z)
        return X

    def fit_transform(self, X, y=None, **fit_params):
        return super().fit_transform(X, y=y, **fit_params)

    def removing_outliers(self, data, column, z=3):
        X = data.copy()

        X["z_score"] = zscore(X[column], nan_policy="omit")

        list_ref = X[(X["z_score"] <= z) & (X["z_score"] >= -z)][column]

        X.loc[X["z_score"] > z, column] = list_ref.max()
        X.loc[X["z_score"] < -z, column] = list_ref.min()

        return X[column]


class CenteredMeanScaler(preprocessing.MinMaxScaler):
    def __init__(self):
        super().__init__()
        self.mean = None

    def fit(self, X, y=None):

        X = X.copy()

        super().fit(X, y)

        self.mean = np.nanmean(super().transform(X))

        return self

    def transform(self, X, y=None):

        X = X.copy()

        X = super().transform(X)

        S = (X - X * self.mean) / (X + self.mean * (1 - 2 * X))

        return S
