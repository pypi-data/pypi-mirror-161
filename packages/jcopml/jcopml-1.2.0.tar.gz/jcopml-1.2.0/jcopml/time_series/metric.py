import numpy as np


def mape(y_true, y_pred):
    mask = y_true != 0
    return (np.fabs(y_true - y_pred) / y_true)[mask].mean()
