import warnings

from sklearn.metrics import mean_squared_error, mean_absolute_error
from tqdm.auto import tqdm

import pandas as pd
from collections import defaultdict

from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from jcopml.time_series.metric import mape


def auto_ets(series, seasonal_periods=None, cv=4, scoring=None, trend="auto", seasonal="auto", damped="auto",
             boxcox="auto"):
    """
    ETS Forecasting with Grid Search and Cross Validation


    == Example usage ==
    model, cv_results = auto_ets(series, seasonal_periods=12)


    == Arguments ==
    series: pandas Series
        time series to decompose

    seasonal_periods: {int, None}
        Periodicity of the sequence. For seasonal, it should be 12.

    cv: int
        Number of cross validation fold

    scoring: str
        If None, mean squared error would be used. Here are list of supported scorer:
        - mse   Mean Squared Error
        - mae   Mean Absolute Error
        - mape  Mean Absolute Percentage Error

    trend: {str, list, None}
        if "auto", then it will be tuned using Grid Search. Here are list of supported trend:
        - add   Additive Trend
        - mul   Multiplicative Trend
        - None  Not using any Trend

        You can also use list of the trend you would want to search in parameter tuning.

    seasonal: {str, list, None}
        if "auto", then it will be tuned using Grid Search. Here are list of supported seasonal:
        - add   Additive Trend
        - mul   Multiplicative Trend
        - None  Not using any Trend

        You can also use list of the seasonal you would want to search in parameter tuning.

    damped: {str, bool}
        if "auto", then it will be tuned using Grid Search.
        if True, then the ETS would utilize damping.

    boxcox: {str, bool}
        if "auto", then it will be tuned using Grid Search.
        if True, then the series would be transformed with boxcox.

    == Return ==
    model
        statsmodels.tsa.holtwinters.HoltWintersResultsWrapper

    cv_results
        pandas DataFrame
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        scoring, scorer = _get_scorer(scoring)
        param_grid = _search_grid(trend, seasonal, damped, boxcox)

        cv_results = defaultdict(lambda: [])
        for trend, seasonal, damped, boxcox in tqdm(param_grid):
            scores = []
            try:
                for fold, (train, val) in enumerate(TimeSeriesSplit(n_splits=cv).split(series)):
                    # CV split
                    train, val = series[train], series[val]

                    # Train
                    s_period = seasonal_periods if seasonal is not None else None
                    es = ExponentialSmoothing(train, trend=trend, seasonal=seasonal, damped=damped,
                                              seasonal_periods=s_period)
                    model = es.fit(optimized=True, use_boxcox=boxcox)

                    # Validate
                    start, end = val.index[0], val.index[-1]
                    pred = model.predict(start, end)
                    score = scorer(val, pred)
                    scores.append(score)

                # Reporting
                cv_results["trend"].append(trend)
                cv_results["seasonal"].append(seasonal)
                cv_results["damped"].append(damped)
                cv_results["boxcox"].append(boxcox)
                for i in range(cv):
                    cv_results[f"{scoring}_{i}"].append(scores[i])
            except:
                continue

        cv_results = pd.DataFrame(cv_results)
        cv_results[f"mean_{scoring}"] = cv_results.loc[:, f"{scoring}_0":].mean(1)
        cv_results.sort_values(f"mean_{scoring}", inplace=True)

        trend, seasonal, damped, boxcox = cv_results.iloc[0, :4].tolist()
        s_period = seasonal_periods if seasonal is not None else None
        es = ExponentialSmoothing(series, trend=trend, seasonal=seasonal, damped=damped, seasonal_periods=s_period)
        model = es.fit(optimized=True, use_boxcox=boxcox)
    return model, cv_results


def _get_scorer(scoring):
    if scoring == "mse":
        scorer = mean_squared_error
    elif scoring == "mae":
        scorer = mean_absolute_error
    elif scoring == "mape":
        scorer = mape
    elif scoring is None:
        scoring = "mse"
        scorer = mean_squared_error
    return scoring, scorer


def _search_grid(trend, seasonal, damped, boxcox):
    if trend == "auto":
        trend_params = [None, "add", "mul"]
    elif isinstance(trend, list):
        trend_params = trend
    elif isinstance(trend, str) or (trend is None):
        trend_params = [trend]

    if seasonal == "auto":
        seasonal_params = [None, "add", "mul"]
    elif isinstance(seasonal, list):
        seasonal_params = seasonal
    elif isinstance(seasonal, str) or (seasonal is None):
        seasonal_params = [seasonal]

    if damped == "auto":
        damped_params = [True, False]
    elif isinstance(damped, bool):
        damped_params = [damped]

    if boxcox == "auto":
        boxcox_params = [True, False]
    elif isinstance(boxcox, bool):
        boxcox_params = [boxcox]

    param_grid = [(trend, seasonal, damped, boxcox)
                  for trend in trend_params
                  for seasonal in seasonal_params
                  for damped in damped_params
                  for boxcox in boxcox_params
                  if not (damped and (trend is None))]
    return param_grid
