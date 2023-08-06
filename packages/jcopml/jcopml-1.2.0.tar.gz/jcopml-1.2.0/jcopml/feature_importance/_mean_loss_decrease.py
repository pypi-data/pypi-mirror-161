import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from xgboost import XGBRegressor, XGBClassifier


def mean_loss_decrease(X_train, model, plot=False, topk=None):
    """
    Function to calculate mean loss decrease. A tree based model must be used to calculate mean loss decrease.
    This is equivalent to scikit-learn's feature importance.


    == Example usage ==
    df_imp = mean_loss_decrease(X_train, model, plot=True)
    df_imp = mean_loss_decrease(X_train, model, plot=True, topk=10)


    == Arguments ==
    X_train: pandas DataFrame
        training input features

    model: scikit-learn pipeline or estimator
        trained scikit-learn pipeline or estimator

    plot: bool
        show feature importance barplot

    topk: int
        number or k most important feature to show in the barplot


    == Return ==
    pandas DataFrame with the features and importance
    """

    cols = _get_cols(X_train, model)
    imp = _get_feature_importance(model)
    df_imp = pd.DataFrame({"feature": cols, "importance": imp}).sort_values("importance", ascending=False)

    if topk:
        df_imp = df_imp.head(topk)

    if plot:
        plt.figure(figsize=(15, 5))
        plt.bar(range(len(df_imp)), df_imp.importance, color='b')
        plt.xticks(range(len(df_imp)), df_imp.feature, rotation=45, horizontalalignment='right')
        plt.ylabel('importance')
        plt.title("Mean Loss Decrease", fontsize=14);
    return df_imp


def _get_cols(X, model):
    steps = model.best_estimator_.named_steps.copy()
    if 'prep' in steps:
        cols = []
        transformers = steps['prep'].transformers_
        steps = steps['prep'].named_transformers_
        for name, pipe, var in transformers:
            if name == 'numeric':
                try:
                    poly = steps['numeric'].named_steps['poly']
                    cols += poly.get_feature_names(input_features=var)
                except (AttributeError, KeyError):
                    cols += var

            if name == 'categoric':
                try:
                    ohe = steps['categoric'].named_steps['onehot']
                    cols += list(pd.get_dummies(X[var], columns=var).columns)
                except (AttributeError, KeyError):
                    cols += var
        return cols
    elif 'poly' in steps:
        poly = steps['poly']
        return poly.get_feature_names(input_features=X.columns)
    else:
        return X.columns


def _get_feature_importance(model):
    algo = model.best_estimator_.steps[-1][1]
    if type(algo) in [RandomForestRegressor, RandomForestClassifier, DecisionTreeRegressor,
                      DecisionTreeClassifier, XGBRegressor, XGBClassifier]:
        return algo.feature_importances_
    else:
        raise Exception("Only supports decision tree, random forest and xgboost")

