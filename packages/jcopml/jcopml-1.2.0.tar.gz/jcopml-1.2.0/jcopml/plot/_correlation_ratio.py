import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_correlation_ratio(df, catvar, numvar, report=False):
    """
    Correlation Ratio heatmap (numerical vs categorical correlation)
    https://en.wikipedia.org/wiki/Correlation_ratio


    == Example usage ==
    from jcopml.plot import plot_correlation_ratio
    plot_correlation_ratio(df, catvar, numvar)
    df_corrat = plot_correlation_ratio(df, catvar, numvar, report=True)


    == Arguments ==
    df: pandas DataFrame
        imported dataset

    catvar: str
        list of categorical columns name

    numvar: list
        list of numerical columns name
    """
    df_corr = df.copy()
    eta_table = {}

    for cat in catvar:
        group_count = df_corr.groupby(cat).count()[numvar]
        group_mean = df_corr.groupby(cat).mean()[numvar]

        total_mean = (group_mean * group_count).sum()
        total_mean = total_mean.divide(group_count.sum())

        std_cat = (group_count * (group_mean - total_mean) ** 2).sum()
        std_num = ((df_corr[numvar] - total_mean) ** 2).sum()
        eta = std_cat / (std_num + 1e-8)
        eta_table[cat] = eta.values

    eta_table = pd.DataFrame(eta_table, index=numvar).T
    sns.heatmap(eta_table, cmap="bwr", vmin=-1, vmax=1, square=True, annot=True,
                fmt=".1f", cbar=False, linewidths=1, linecolor='k')
    plt.xticks(rotation=45, horizontalalignment='right')
    plt.yticks(rotation=0, verticalalignment='center')
    plt.title(f"Correlation Ratio", fontsize=14)
    plt.ylabel("Categorical Columns", fontsize=14)
    plt.xlabel("Numerical Columns", fontsize=14)

    if report:
        return eta_table

