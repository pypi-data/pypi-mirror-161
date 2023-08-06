import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_missing_value(df, return_df=False, feature_alignment='horizontal', figsize=(15, 8)):
    """
    Missing value heatmap


    == Example usage ==
    from jcopml.plot import plot_missing_value
    plot_missing_value(df)
    df_miss = plot_missing_value(df, return_df=True)


    == Arguments ==
    df: pandas DataFrame
        imported dataset

    return_df: bool
        If true, then report DataFrame is returned

    feature_alignment: {'vertical', 'horizontal', 'column', 'row'} or {'v', 'h', 'c', 'r'}
        direction to align the features

    figsize: (int, int)
        figure size


    == Return ==
    pandas DataFrame if return_df is True, else None
    """
    plt.figure(figsize=figsize)
    if feature_alignment in ['vertical', 'v', 'column', 'c']:
        sns.heatmap(~df.isna(), cbar=False, cmap="Blues")
    elif feature_alignment in ['horizontal', 'h', 'row', 'r']:
        sns.heatmap(~df.isna().T, cbar=False, cmap="Blues")
    else:
        raise Exception("Supported alignment {'vertical', 'horizontal', 'column', 'row'} or {'v', 'h', 'c', 'r'}")
    plt.xticks(rotation=45, horizontalalignment='right');
    if return_df:
        df_miss = pd.DataFrame(df.isna().sum(), columns=['missing_value'])
        df_miss["%"] = round(df_miss/len(df)*100, 2)
        return df_miss
