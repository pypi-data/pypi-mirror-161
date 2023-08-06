import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from jcopml.plot import plot_confusion_matrix, plot_actual_vs_prediction, plot_residual

from jcopml.feature_importance import mean_score_decrease

from jcopml.utils import save_model

from sklearn.impute import KNNImputer, SimpleImputer

from jcopml.pipeline import num_pipe, cat_pipe
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline

from jcopml.tuning.skopt import BayesSearchCV
from jcopml.automl._automl_params import autoreg_params, autoclf_params, _reg_algo, _clf_algo


class AutoBase:
    def __init__(self):
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        self.model = None
        self.best_estimators_ = None
        self.cv_results = None
        self.search_mode = None

    def predict(self, X):
        return self.best_estimators_.predict(X)

    def save(self, fname="model.pkl", outdir="model", estimator_only=True):
        if estimator_only:
            save_model(self.best_estimators_, fname, folder_name=outdir)
        else:
            save_model(self, fname, folder_name=outdir)

    def plot_results(self):
        df = self.cv_results
        plt.figure(figsize=(15, 5))
        plt.bar(np.arange(0, len(df)) - 0.125, df.mean_train_score, yerr=df.std_train_score, color='turquoise',
                error_kw={"capsize": 5}, width=0.25, label="Train")
        plt.bar(np.arange(0, len(df)) + 0.125, df.mean_test_score, yerr=df.std_test_score, color='lightblue',
                error_kw={"capsize": 5}, width=0.25, label="Test")
        plt.xticks(np.arange(0, len(df)), df.algo, horizontalalignment='center', fontsize=12)
        plt.ylabel(f'{self.model.scoring}', fontsize=14)

        if self.search_mode == "random":
            plt.title("Best results sorted by Mean Test Score", fontsize=14);
        elif self.search_mode == "bayes":
            plt.title("Top 5 Best results by Mean Test Score", fontsize=14);
        plt.legend(ncol=2, loc="upper right")

    def mean_score_decrease(self, plot=True, topk=10):
        df_imp = mean_score_decrease(self.X_train, self.y_train, self.best_estimators_, plot=plot, topk=topk)
        if not plot:
            return df_imp

    def report(self):
        print("================== Best Model Info ==================")
        for k, v in self.model.best_params_.items():
            if k.startswith("algo"):
                if k == "algo":
                    print(f"{k:25} | {v.__class__.__name__}")
                else:
                    print(f"{k:25} | {v}")
        print("=====================================================")
        print("")
        print("================================ Best Preprocessor Info =================================")
        for k, v in self.model.best_params_.items():
            if k.startswith("prep"):
                if k == "prep__numeric":
                    for k2, v2 in _parse_prep_numeric(v):
                        print(f"{k2:25} | {v2}")
                elif k == "prep__categoric":
                    for k2, v2 in _parse_prep_categoric(v):
                        print(f"{k2:25} | {v2}")
        print("=========================================================================================")
        print("")
        print("=========== Score ===========")
        if self.model.return_train_score:
            print(f"Train: {self.cv_results.mean_train_score.iloc[0]}")
        print(f"Valid: {self.cv_results.mean_test_score.iloc[0]}")
        print(f"Test : {self.model.score(self.X_test, self.y_test)}")
        print("=============================")

    def _cv_results(self):
        if self.search_mode == "random":
            df = pd.DataFrame(self.model.cv_results_)
            df["algo"] = df.param_algo.apply(lambda x: x.__class__.__name__)
            best_rank = df.groupby("algo").rank_test_score.idxmin()
            df = df.loc[best_rank, "split0_test_score":"algo"]
            df.sort_values("mean_test_score", ascending=False, inplace=True)
        elif self.search_mode == "bayes":
            df = pd.DataFrame.from_dict(self.model.cv_results_, orient="index").T
            df.sort_values("mean_test_score", ascending=False, inplace=True)
            df = df.iloc[:5]

            algo = df.param_algo.apply(lambda x: x.__class__.__name__)
            train = df.loc[:, "split0_train_score": "std_train_score"]
            test = df.loc[:, "split0_test_score": "std_test_score"]

            df = train.join(test)
            df["algo"] = algo
        return df


class AutoRegressor(AutoBase):
    def __init__(self, num_feature, cat_feature, processed_num_feature=[], processed_cat_feature=[], random_state=42):
        """
        Quick way to create a regression benchmark.


        == Example usage ==
        automl = AutoRegressor(["col1", "col2"], ["col3", "col4"])
        model = automl.fit(X, y)


        == Arguments ==
        num_feature: list of str
            list of numerical column names in the dataframe

        cat_feature: list of str
            list of categorical column names in the dataframe (Would be OneHot encoded)

        processed_num_feature; list of str
            list of numerical column to be used as is (except for imputation)

        processed_cat_feature; list of str
            list of ordinal categorical column to be used as is (except for imputation)

        random_state: int or None
            random state for parameter search
        """
        super().__init__()
        self.preprocessor = ColumnTransformer([
            ('numeric', num_pipe(), num_feature),
            ('categoric', cat_pipe(encoder="onehot"), cat_feature),
            ('proc_numeric', num_pipe(), processed_num_feature),
            ('proc_categoric', cat_pipe(), processed_cat_feature)
        ])
        self.random_state = random_state

    def fit(self, X, y, test_size=0.2, algo="all", search_mode="random", poly=False, scaling=True, cv=3, n_trial=50,
            scoring=None, ret_train_score=True):
        f"""
        == Arguments ==
        X: numpy or pandas DataFrame
            input features
        y: numpy or pandas DataFrame
            target
        test_size: float
            test split ratio used in sklearn train_test_split
        algo: list or str
            list of algo to use.
            Available algorithms: {_reg_algo}
            - input "all" to use all available algorithms.
            - input "tree" to use only tree-based algorithms
        search_mode: {"random", "bayes"}
            Perform parameter search.
            - random: RandomizedSearchCV
            - bayes: BayesSearchCV
        poly: bool
            Set poly=True to consider polynomial features in parameter search
        scaling: bool
            Set scaling=True to consider scaling and transformation in parameter search
        cv: int or sklearn Split object
            cross validation fold. See: RandomizedSearchCV or BayesSearchCV
        n_trial: int
            number of search trial / iteration
        scoring: str
            scoring parameter as in scikit-learn.
            See: https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter
        ret_train_score: bool
            whether to return the train score or not

        == Return ==
        scikit-learn model (SearchCV object)
        """
        self.search_mode = search_mode
        if isinstance(algo, str) and algo not in ["all", "tree"]:
            algo = [algo]

        if scoring is None:
            scoring = "r2"

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size,
                                                                                random_state=self.random_state)

        pipeline = Pipeline([
            ("prep", self.preprocessor),
            ('algo', DummyRegressor())
        ])

        cv_algo = RandomizedSearchCV if search_mode == "random" else BayesSearchCV
        model = cv_algo(pipeline, autoreg_params(algo, search_mode, poly, scaling), cv=cv, n_iter=n_trial, n_jobs=-1,
                        scoring=scoring, verbose=1, return_train_score=ret_train_score, random_state=self.random_state)
        model.fit(self.X_train, self.y_train)

        self.model = model
        self.best_estimators_ = model.best_estimator_
        self.cv_results = self._cv_results()
        self.report()

    def plot_actual_vs_prediction(self):
        plot_actual_vs_prediction(self.X_train, self.y_train, self.X_test, self.y_test, self.model)

    def plot_residual(self, lowess=False):
        """
        Residual plot

        lowess: bool
            include the LOWESS (Locally Weighted Scatterplot Smoothing) line
        """
        plot_residual(self.X_train, self.y_train, self.X_test, self.y_test, self.model, lowess=lowess)


class AutoClassifier(AutoBase):
    def __init__(self, num_feature, cat_feature, processed_num_feature=[], processed_cat_feature=[], random_state=42):
        """
        Quick way to create a classification benchmark.


        == Example usage ==
        automl = AutoClassifier(["col1", "col2"], ["col3", "col4"])
        model = automl.fit(X, y)


        == Arguments ==
        num_feature: list of str
            list of numerical column names in the dataframe

        cat_feature: list of str
            list of categorical column names in the dataframe (Would be OneHot encoded)

        processed_num_feature; list of str
            list of numerical column to be used as is (except for imputation)

        processed_cat_feature; list of str
            list of ordinal categorical column to be used as is (except for imputation)

        random_state: int or None
            random state for parameter search
        """
        super().__init__()
        self.preprocessor = ColumnTransformer([
            ('numeric', num_pipe(), num_feature),
            ('categoric', cat_pipe(encoder="onehot"), cat_feature),
            ('proc_numeric', num_pipe(), processed_num_feature),
            ('proc_categoric', cat_pipe(), processed_cat_feature)
        ])
        self.random_state = random_state

    def fit(self, X, y, test_size=0.2, algo="all", search_mode="random", poly=False, scaling=True, cv=3, n_trial=50,
            scoring=None, ret_train_score=True):
        f"""
        == Arguments ==
        X: numpy or pandas DataFrame
            input features
        y: numpy or pandas DataFrame
            target
        test_size: float
            test split ratio used in sklearn train_test_split
        algo: list or str
            list of algo to use.
            Available algorithms: {_clf_algo}
            - input "all" to use all available algorithms.
            - input "tree" to use only tree-based algorithms.
        search_mode: {"random", "bayes"}
            Perform parameter search.
            - random: RandomizedSearchCV
            - bayes: BayesSearchCV
        poly: bool
            Set poly=True to consider polynomial features in parameter search
        scaling: bool
            Set scaling=True to consider scaling and transformation in parameter search
        cv: int or sklearn Split object
            cross validation fold. See: RandomizedSearchCV or BayesSearchCV
        n_trial: int
            number of search trial / iteration
        scoring: str
            scoring parameter as in scikit-learn.
            See: https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter
        ret_train_score: bool
            whether to return the train score or not

        == Return ==
        scikit-learn model (SearchCV object)
        """
        self.search_mode = search_mode
        if isinstance(algo, str) and algo not in ["all", "tree"]:
            algo = [algo]

        if scoring is None:
            scoring = "accuracy"

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size, stratify=y,
                                                                                random_state=self.random_state)

        pipeline = Pipeline([
            ("prep", self.preprocessor),
            ('algo', DummyRegressor())
        ])

        cv_algo = RandomizedSearchCV if search_mode == "random" else BayesSearchCV
        model = cv_algo(pipeline, autoclf_params(algo, search_mode, poly, scaling), cv=cv, n_iter=n_trial, n_jobs=-1,
                        scoring=scoring, verbose=1, return_train_score=ret_train_score, random_state=self.random_state)
        model.fit(self.X_train, self.y_train)

        self.model = model
        self.best_estimators_ = model.best_estimator_
        self.cv_results = self._cv_results()
        self.report()

    def plot_confusion_matrix(self):
        plot_confusion_matrix(self.X_train, self.y_train, self.X_test, self.y_test, self.model)


def _parse_prep_numeric(pipe):
    params = pipe.get_params()
    result = {}
    for k, v in params.items():
        if k == "imputer":
            name = v.__class__.__name__
            if isinstance(v, KNNImputer):
                result["numerical_imputer"] = f"{name}(add_indicator={v.add_indicator}, n_neighbors={v.n_neighbors})"
            elif isinstance(v, SimpleImputer):
                result["numerical_imputer"] = f"{name}(add_indicator={v.add_indicator}, strategy='{v.strategy}')"
        elif k == "poly":
            name = v.__class__.__name__
            result["numerical_poly"] = name
        elif k == "transformer":
            name = v.__class__.__name__
            result["numerical_transformer"] = f"{name}(method='{v.method}')"
        elif k == "scaler":
            name = v.__class__.__name__
            result["numerical_scaler"] = name
    return result.items()


def _parse_prep_categoric(pipe):
    params = pipe.get_params()
    result = {}
    for k, v in params.items():
        if k == "imputer":
            name = v.__class__.__name__
            result["categorical_imputer"] = f"{name}(add_indicator={v.add_indicator}, strategy='{v.strategy}')"
        elif k == "onehot":
            result["categorical_encoder"] = v.__class__.__name__
    return result.items()
