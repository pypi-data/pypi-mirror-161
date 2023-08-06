import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix


def plot_confusion_matrix(X_train, y_train, X_test, y_test, model):
    """
    Confusion Matrix heatmap


    == Example usage ==
    from jcopml.plot import plot_classification_report
    plot_confusion_matrix(X_train, y_train, X_test, y_test, model)


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
    labels = model.classes_

    plt.figure(figsize=(11, 5))

    plt.subplot(121)
    cm = confusion_matrix(y_train, model.predict(X_train), labels=labels)
    sns.heatmap(cm, annot=True, square=True, cmap='Blues', cbar=False, xticklabels=labels, yticklabels=labels,
                fmt="d", annot_kws={"fontsize": 15})
    plt.title(f'Train score: {model.score(X_train, y_train):.3f}', fontsize=14)
    plt.xlabel('Prediction', fontsize=14)
    plt.ylabel('Actual', fontsize=14)
    plt.yticks(rotation=0, verticalalignment='center')

    plt.subplot(122)
    cm = confusion_matrix(y_test, model.predict(X_test), labels=labels)
    sns.heatmap(cm, annot=True, square=True, cmap='Greens', cbar=False, xticklabels=labels, yticklabels=labels,
                fmt="d", annot_kws={"fontsize": 15})
    plt.title(f'Test score: {model.score(X_test, y_test):.3f}', fontsize=14)
    plt.xlabel('Prediction', fontsize=14)
    plt.ylabel('Actual', fontsize=14)
    plt.yticks(rotation=0, verticalalignment='center');
