import matplotlib.pyplot as plt
import seaborn as sns


def plot_residual(X_train, y_train, X_test, y_test, model, lowess=False):
    """
    Residual plot


    == Example usage ==
    from jcopml.plot import plot_residual
    plot_residual(X_train, y_train, X_test, y_test, model)


    == Arguments ==
    X_train, X_test: pandas DataFrame
        training and testing input features

    y_train, y_test: pandas Series
        training and testing labels

    model: scikit-learn pipeline or estimator
        trained scikit-learn pipeline or estimator

    lowess: bool
        include the LOWESS (Locally Weighted Scatterplot Smoothing) line

    == Return ==
    None
    """
    plt.figure(figsize=(15, 5))

    plt.subplot(121)
    sns.residplot(x=model.predict(X_train), y=y_train, lowess=lowess, scatter_kws={'s': 10, 'color': 'b'})
    plt.xlabel("Prediction", fontsize=14)
    plt.ylabel("Residual", fontsize=14)
    plt.title("Train")

    plt.subplot(122)
    sns.residplot(x=model.predict(X_test), y=y_test, lowess=lowess, scatter_kws={'s': 10, 'color': 'b'})
    plt.xlabel("Prediction", fontsize=14)
    plt.ylabel("Residual", fontsize=14)
    plt.title("Test");
