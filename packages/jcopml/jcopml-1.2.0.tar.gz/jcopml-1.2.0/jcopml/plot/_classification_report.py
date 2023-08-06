import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report


def plot_classification_report(X_train, y_train, X_test, y_test, model, report=False, return_df=False):
    """
    Classification report as in scikit-learn's metrics


    == Example usage ==
    from jcopml.plot import plot_classification_report
    plot_classification_report(X_train, y_train, X_test, y_test, model)
    plot_classification_report(X_train, y_train, X_test, y_test, model, report=True)
    df_report = plot_classification_report(X_train, y_train, X_test, y_test, model, return_df=True)


    == Arguments ==
    X_train, X_test: pandas DataFrame
        training and testing input features

    y_train, y_test: pandas Series
        training and testing labels

    model: scikit-learn pipeline or estimator
        trained scikit-learn pipeline or estimator

    report: bool
        If True, then return a simple print of the classification report. If False, then a seaborn heatmap is returned

    return_df: bool
        If True, then return a pandas dataframe of the report. This argument is neglected if report is True

    == Return ==
    (pandas DataFrame, pandas DataFrame) if return_df is True, else None is returned
    """
    if report:
        print("Train report")
        print(classification_report(y_train, model.predict(X_train)))
        print()
        print("Test report")
        print(classification_report(y_test, model.predict(X_test)))
    else:
        plt.figure(figsize=(11, 5))
        plt.subplots_adjust(wspace=0.4)

        plt.subplot(121)
        labels = y_train.unique()
        df_train = pd.DataFrame(classification_report(y_train, model.predict(X_train), labels=labels, output_dict=True))
        df_plot = df_train.iloc[:-1, :len(labels)]
        sns.heatmap(df_plot, vmin=0, vmax=1, annot=True, square=True, cmap='Blues', cbar=False, xticklabels=labels,
                    yticklabels=df_plot.index, fmt=".2f", annot_kws={"fontsize": 15})
        plt.yticks(rotation=0, fontsize=14)
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=12)
        plt.title("Train", fontsize=14)

        plt.subplot(122)
        labels = y_test.unique()
        df_test = pd.DataFrame(classification_report(y_test, model.predict(X_test), labels=labels, output_dict=True))
        df_plot = df_test.iloc[:-1, :len(labels)]
        sns.heatmap(df_plot, vmin=0, vmax=1, annot=True, square=True, cmap='Greens', cbar=False, xticklabels=labels,
                    yticklabels=df_plot.index, fmt=".2f", annot_kws={"fontsize": 15})
        plt.yticks(rotation=0, fontsize=14)
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=12)
        plt.title("Test", fontsize=14)

        if return_df:
            return df_train.T, df_test.T
