import numpy as np
import matplotlib.pyplot as plt


def plot_svc(X, y, model, support=True):
    """
    Support Vector Classifier (SVC) decision plot
    Only support 2 input features (2D plot)


    == Example usage ==
    from jcopml.plot import plot_svc
    plot_svc(X, y, model)
    plot_svc(X, y, model, support=True)


    == Arguments ==
    X: pandas DataFrame
        input features

    y: pandas Series
        target labels

    model: scikit-learn pipeline or estimator
        trained scikit-learn pipeline or estimator

    support: bool
        highlight support vectors

    == Return ==
    None
    """
    assert X.shape[1] == 2

    plt.figure(figsize=(6, 6))
    plt.scatter(X.iloc[:, 0], X.iloc[:, 1], c=y, s=5, cmap='bwr')

    xlim = plt.xlim()
    ylim = plt.ylim()

    xx = np.linspace(xlim[0], xlim[1], 50)
    yy = np.linspace(ylim[0], ylim[1], 50)
    X, Y = np.meshgrid(xx, yy)

    xy = np.c_[X.ravel(), Y.ravel()]
    val = model.decision_function(xy).reshape(X.shape)

    if support:
        x_sv = model.support_vectors_[:, 0]
        y_sv = model.support_vectors_[:, 1]
        plt.scatter(x_sv, y_sv, s=90, linewidth=1, edgecolor='k', facecolor='None')
        plt.contour(X, Y, val, colors='k', levels=[-1, 0, 1], alpha=0.5, linestyles=['-', '--', '-'])
    else:
        plt.contour(X, Y, val, colors='k', levels=[0], alpha=0.5, linestyles=['-'])
