import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ipywidgets import interact, ToggleButtons
from sklearn.preprocessing import PowerTransformer


def plot_correlation_matrix(df, target_col, numeric_col='auto'):
    """
    Correlation matrix widget


    == Example usage ==
    from jcopml.plot import plot_correlation_matrix
    plot_correlation_matrix(df, target_col, numeric_col='auto')


    == Arguments ==
    df: pandas DataFrame
        imported dataset

    target_col: str
        target column name

    numeric_col: list or 'auto'
        list of numerical columns name, or specify 'auto' to use pandas select_dtypes


    == Return ==
    None
    """
    def _simul_method(method='spearman'):
        def _simul(threshold=0):
            # config
            linewidth = 1
            linecolor = 'k'
            mask_feature = None
            mask_target = None

            # masking
            if threshold > 0:
                mask_feature = (feature_corr < threshold) & (feature_corr > -threshold)
                mask_target = (target_corr < threshold) & (target_corr > -threshold)

            # plot
            plt.figure(figsize=(15, 7))

            plt.subplot(121)
            sns.heatmap(feature_corr, mask=mask_feature, cmap="bwr", vmin=-1, vmax=1, square=True, annot=True, fmt=".1f",
                        cbar=False, linewidths=linewidth, linecolor=linecolor)
            plt.xticks(rotation=45, horizontalalignment='right')
            plt.title(f"Feature correlation\n({method.upper()})", fontsize=14)
            plt.axhline(y=0, color='k', linewidth=1)
            plt.axhline(y=feature_corr.shape[1], color='k', linewidth=1)
            plt.axvline(x=0, color='k', linewidth=1)
            plt.axvline(x=feature_corr.shape[0], color='k', linewidth=1)

            plt.subplot(122)
            sns.heatmap(target_corr, mask=mask_target, cmap="bwr", vmin=-1, vmax=1, square=True, annot=True, fmt=".1f",
                        cbar=False, linewidths=linewidth, linecolor=linecolor)
            plt.xticks(rotation=45, horizontalalignment='right')
            plt.title(f"Target correlation\n({method.upper()})", fontsize=14)
            plt.axhline(y=0, color='k', linewidth=1)
            plt.axhline(y=feature_corr.shape[1], color='k', linewidth=1)
            plt.axvline(x=0, color='k', linewidth=1)
            plt.axvline(x=feature_corr.shape[0], color='k', linewidth=1);

        df_corr = df.copy()
        df_corr = df_corr[num_col]

        if method == 'pearson_norm':
            power = PowerTransformer(standardize=False)
            df_corr.iloc[:, :] = power.fit_transform(df_corr)
            method = 'pearson'

        # Separate feature and target correlation
        corr = df_corr.corr(method=method)
        feature_corr = corr.drop(columns=target_col, index=target_col)
        target_corr = corr[[target_col]].drop(index=target_col)
        interact(_simul, threshold=(0, 1, 0.1))

    if isinstance(numeric_col, list):
        num_col = numeric_col.copy()
        if target_col not in num_col:
            num_col += [target_col]
    elif numeric_col == "auto":
        num_col = list(df.select_dtypes(np.number).columns)
    else:
        raise Exception("numeric_col should be a list of columns name or 'auto'")

    # Remove single constant column
    tmp = df[num_col].std()
    single_constant_col = list(tmp[tmp == 0].index)
    if single_constant_col:
        raise ValueError(f"Feature should not have a constant value\n"
                         f"You should remove these column from your data -> {', '.join(single_constant_col)}")
    interact(_simul_method, method=ToggleButtons(description='method',
                                                 options=['spearman', 'kendall', 'pearson', 'pearson_norm']))
