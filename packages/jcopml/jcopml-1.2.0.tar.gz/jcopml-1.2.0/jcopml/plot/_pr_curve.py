import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, average_precision_score, auc


def plot_pr_curve(X_train, y_train, X_test, y_test, model):
    """
    Precision-recall curve plot


    == Example usage ==
    from jcopml.plot import plot_pr_curve
    plot_pr_curve(X_train, y_train, X_test, y_test, model)


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
    p, r, t_pr = precision_recall_curve(y_train, prob)
    AP = average_precision_score(y_train, prob)
    plt.plot(r, p, 'b-')
    plt.title(f"Train PR_AUC: {auc(r, p):.3f} | AP: {AP:.3f}", fontsize=14)
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    plt.xlabel("Recall")
    plt.ylabel("Precision")

    plt.subplot(122)
    prob = model.predict_proba(X_test)[:, 1]
    p, r, t_pr = precision_recall_curve(y_test, prob)
    AP = average_precision_score(y_test, prob)
    plt.plot(r, p, 'b-')
    plt.title(f"Test PR_AUC: {auc(r, p):.3f} | AP: {AP:.3f}", fontsize=14)
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    plt.xlabel("Recall")
    plt.ylabel("Precision");
