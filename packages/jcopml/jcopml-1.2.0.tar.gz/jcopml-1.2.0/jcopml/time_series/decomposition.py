import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose, STL


def additive_decomposition(series, plot=False, period=None, center=True, extrapolate_trend=False):
    """
    Additive Time Series Decomposition with Moving Average


    == Example usage ==
    components = additive_decomposition(series)


    == Arguments ==
    series: pandas Series
        time series to decompose

    plot: bool
        if True, then trend, seasonality, and residual plot is shown.

    period: int
        Periodicity of the sequence. For seasonal, it should be 12.

    center: bool
        If True, then centered window will be used

    extrapolate_trend: bool
        If True, trend is extrapolated to match observed series

    == Return ==
    statsmodels.tsa.seasonal.DecomposeResult
    """
    components = seasonal_decompose(series, model="additive", period=period, two_sided=center,
                                    extrapolate_trend=extrapolate_trend)
    if plot:
        _plot_decomposition(components, "additive")
    return components


def multiplicative_decomposition(series, plot=False, period=None, center=True, extrapolate_trend=False):
    """
    Multiplicative Time Series Decomposition with Moving Average


    == Example usage ==
    components = multiplicative_decomposition(series)


    == Arguments ==
    series: pandas Series
        time series to decompose

    plot: bool
        if True, then trend, seasonality, and residual plot is shown.

    period: int
        Periodicity of the sequence. For seasonal, it should be 12.

    center: bool
        If True, then centered window will be used

    extrapolate_trend: bool
        If True, trend is extrapolated to match observed series

    == Return ==
    statsmodels.tsa.seasonal.DecomposeResult
    """
    components = seasonal_decompose(series, model="multiplicative", period=period, two_sided=center,
                                    extrapolate_trend=extrapolate_trend)
    if plot:
        _plot_decomposition(components, "multiplicative")
    return components


def stl_decomposition(series, plot=False, period=None, seasonal_smoothing=13, trend_smoothing=None, robust=False, *args, **kwargs):
    """
    Seasonal-Trend Decomposition with LOESS

    For more detail on each parameters, please check statsmodels documentation here
        https://www.statsmodels.org/dev/examples/notebooks/generated/stl_decomposition.html

    == Example usage ==
    components = stl_decomposition(series)


    == Arguments ==
    series: pandas Series
        time series to decompose

    plot: bool
        if True, then trend, seasonality, and residual plot is shown.

    period: int
        Periodicity of the sequence. For seasonal, it should be 12.

    seasonal_smoothing : int
        Length of the seasonal smoother. Must be an odd integer, and should normally be >= 7.

    trend_smoothing : {int, None}
        Length of the trend smoother. Must be an odd integer. If not provided
        uses the smallest odd integer greater than 1.5 * period, following the
        suggestion in the original implementation.

    robust: bool
        Use weight to handle outliers


    == Return ==
    statsmodels.tsa.seasonal.DecomposeResult
    """

    components = STL(series, period=period, seasonal=seasonal_smoothing, trend=trend_smoothing, robust=robust, *args, **kwargs).fit()
    if plot:
        _plot_decomposition(components, "stl")
    return components


def _plot_decomposition(components, model):
    F_t = max(0, 1 - components.resid.var() / (components.trend + components.resid).var())
    F_s = max(0, 1 - components.resid.var() / (components.seasonal + components.resid).var())

    if model == "multiplicative":
        ax_line = 1
    else:
        ax_line = 0

    fig, ax = plt.subplots(4, 1, sharex=True, figsize=(15, 10))
    fig.subplots_adjust(hspace=0.05)

    ax[0].plot(components.observed, "b-")
    ax[0].plot(components.trend, "r-")
    ax[0].set_ylabel("Observed", fontsize=14)
    ax[0].set_title(f"Strength of Trend: {F_t:.2f} | Strength of Seasonality: {F_s:.2f}", fontsize=14)
    ax[1].plot(components.trend, "r-")
    ax[1].set_ylabel("Trend", fontsize=14)
    ax[2].plot(components.seasonal, "g-")
    ax[2].set_ylabel("Seasonal", fontsize=14)
    ax[3].plot(components.resid, "mo", markersize=5)
    ax[3].axhline(ax_line, color="k", linewidth=1, linestyle="dashed", zorder=-1)
    ax[3].set_ylabel("Residual", fontsize=14);
