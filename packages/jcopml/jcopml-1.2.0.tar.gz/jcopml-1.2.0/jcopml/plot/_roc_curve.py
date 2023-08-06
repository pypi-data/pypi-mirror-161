import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc


def plot_roc_curve(X_train, y_train, X_test, y_test, model):
    """
    Receiver Operating Characteristic (ROC) Curve
    ROC curve is TPR vs FPR plot


    == Example usage ==
    from jcopml.plot import plot_roc_curve
    plot_roc_curve(X_train, y_train, X_test, y_test, model)


    == Arguments ==
    X_train, X_test: pandas DataFrame
        training and testing input features

    y_train, y_test: pandas Series
        training and testing labels

    model: scikit-learn pipeline or estimator
        trained scikit-learn pipeline or estimator


    == Return ==
    None
    """
    plt.figure(figsize=(13, 6))

    plt.subplot(121)
    prob = model.predict_proba(X_train)[:, 1]
    fpr, tpr, t_roc = roc_curve(y_train, prob)
    plt.plot(fpr, tpr, 'b-')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title(f"Train ROC_AUC: {auc(fpr, tpr):.3f}", fontsize=14)
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    plt.xlabel("FPR")
    plt.ylabel("TPR")

    plt.subplot(122)
    prob = model.predict_proba(X_test)[:, 1]
    fpr, tpr, t_roc = roc_curve(y_test, prob)
    plt.plot(fpr, tpr, 'b-')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title(f"Test ROC_AUC: {auc(fpr, tpr):.3f}", fontsize=14)
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    plt.xlabel("FPR")
    plt.ylabel("TPR")
