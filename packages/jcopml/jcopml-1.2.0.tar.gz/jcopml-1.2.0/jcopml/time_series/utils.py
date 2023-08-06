import warnings
import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


def stationarity_tester(time_series, dropna=True):
    if dropna:
        time_series = time_series.dropna()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df_adf = _adf_test(time_series)
        df_kpss = _kpss_test(time_series)

    df = pd.concat([df_adf, df_kpss], axis=1, sort=False).T
    _adf, _kpss = df.reject_null = df.reject_null.astype(bool)

    if _adf:
        print("ADF:        Series is stationary")
    else:
        print("ADF:        Series is non-stationary")

    if _kpss:
        print("KPSS:       Series is non-stationary")
    else:
        print("KPSS:       Series is trend stationary")

    if _adf and _kpss:
        print("Conclusion: Series may be difference stationary. Try using differencing.")
    elif (not _adf) and _kpss:
        print("Conclusion: Series is non-stationary")
    elif _adf and (not _kpss):
        print("Conclusion: Series is stationary")
    else:
        print("Conclusion: Series is trend stationary. Try detrending the series.")
    return df


def _adf_test(time_series):
    adf, p_value, used_lag, n_obs, crit_values, best_ic = adfuller(time_series)
    df = pd.Series([adf, p_value], index=['Test Statistic', 'p-value'], name="ADF")
    for k, v in crit_values.items():
        df[f'Critical Value ({k})'] = v
    df["reject_null"] = (p_value <= 0.05)
    return df


def _kpss_test(time_series):
    kpss_, p_value, used_lag, crit_values = kpss(time_series, nlags="auto")
    df = pd.Series([kpss_, p_value], index=['Test Statistic', 'p-value'], name="KPSS")
    for k, v in crit_values.items():
        if k != "2.5%":
            df[f'Critical Value ({k})'] = v
    df["reject_null"] = (p_value <= 0.05)
    return df


def plot_acf_pacf(series, figsize=(15, 8), dropna=True):
    if dropna:
        series = series.dropna()

    plt.figure(figsize=figsize)
    plt.subplot(211)
    plt.plot(series, "b-")

    ax1 = plt.subplot(223)
    plot_acf(series, lags=50, ax=ax1, title="ACF", color="b", alpha=None);

    ax2 = plt.subplot(224)
    plot_pacf(series, lags=50, ax=ax2, title="PACF", color="r", alpha=None);
