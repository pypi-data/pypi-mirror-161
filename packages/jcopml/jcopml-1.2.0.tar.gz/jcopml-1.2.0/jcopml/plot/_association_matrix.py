from collections import Counter

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, entropy
import matplotlib.pyplot as plt
import seaborn as sns
from ipywidgets import interact, ToggleButtons


def plot_association_matrix(df, target_col, categoric_col='auto'):
    """
    Association matrix widget
    

    == Example usage ==
    from jcopml.plot import plot_association_matrix
    plot_association_matrix(df, target_col, categoric_col='auto')


    == Arguments ==
    df: pandas DataFrame
        imported dataset

    target_col: str
        target column name

    categoric_col: list or 'auto'
        list of categorical columns name, or specify 'auto' to use pandas select_dtypes


    == Return ==
    None
    """

    def _simul_method(method="Cramer's V"):
        def _simul(threshold=0, ):
            # config
            linewidth = 1
            linecolor = 'k'
            mask_feature = None
            mask_target = None

            # masking
            if threshold > 0:
                mask_feature = (feature_assoc < threshold) & (feature_assoc > -threshold)
                mask_target = (target_assoc < threshold) & (target_assoc > -threshold)

            # plot
            plt.figure(figsize=(15, 7))

            plt.subplot(121)
            sns.heatmap(feature_assoc, mask=mask_feature, cmap="bwr", vmin=-1, vmax=1, square=True, annot=True,
                        fmt=".1f",
                        cbar=False, linewidths=linewidth, linecolor=linecolor)
            plt.xticks(rotation=45, horizontalalignment='right')
            plt.title(f"Feature Association\n({method.upper()})", fontsize=14)
            plt.axhline(y=0, color='k', linewidth=1)
            plt.axhline(y=feature_assoc.shape[1], color='k', linewidth=1)
            plt.axvline(x=0, color='k', linewidth=1)
            plt.axvline(x=feature_assoc.shape[0], color='k', linewidth=1)

            plt.subplot(122)
            sns.heatmap(target_assoc, mask=mask_target, cmap="bwr", vmin=-1, vmax=1, square=True, annot=True, fmt=".1f",
                        cbar=False, linewidths=linewidth, linecolor=linecolor)
            plt.xticks(rotation=45, horizontalalignment='right')
            plt.title(f"Target Association\n({method.upper()})", fontsize=14)
            plt.axhline(y=0, color='k', linewidth=1)
            plt.axhline(y=feature_assoc.shape[1], color='k', linewidth=1)
            plt.axvline(x=0, color='k', linewidth=1)
            plt.axvline(x=feature_assoc.shape[0], color='k', linewidth=1);

        df_corr = df.copy()
        df_corr = df_corr[cat_col]

        # Separate feature and target association
        assoc = AssociationDataframe(df_corr).assoc(method=method)
        feature_assoc = assoc.drop(columns=target_col, index=target_col)
        target_assoc = assoc[[target_col]].drop(index=target_col)

        interact(_simul, threshold=(0, 1, 0.1))

    if isinstance(categoric_col, list):
        cat_col = categoric_col.copy()
        if target_col not in cat_col:
            cat_col += [target_col]
    elif categoric_col == 'auto':
        cat_col = list(df.select_dtypes(include=['bool', 'object']).columns)
    else:
        raise Exception("categoric_col should be a list of columns name or 'auto'")

    # Remove single category column
    tmp = df[cat_col].nunique()
    single_category_col = list(tmp[tmp == 1].index)
    if single_category_col:
        raise ValueError(f"Categorical column should have at least 2 category\n"
                         f"You should remove these column from your data -> {', '.join(single_category_col)}")

    interact(_simul_method, method=ToggleButtons(description='method',
                                                 options=["Cramer's V", "Proficiency U(X|Y)", "Proficiency U(Y|X)",
                                                          "Symmetric Proficiency"]))


class AssociationDataframe:
    def __init__(self, df):
        self.n = len(df)
        self.df = df.copy()
        self.cat_col = df.columns

    def assoc(self, method):
        assc = {var: {} for var in self.cat_col}
        for i, v1 in enumerate(self.cat_col):
            for v2 in self.cat_col[i:]:
                if method == "Cramer's V":
                    assc[v1][v2] = assc[v2][v1] = self.cramers_v(v1, v2)
                elif method == "Proficiency U(X|Y)":
                    assc[v1][v2] = self.proficiency(v1, v2)
                    assc[v2][v1] = self.proficiency(v2, v1)
                elif method == "Proficiency U(Y|X)":
                    assc[v1][v2] = self.proficiency(v2, v1)
                    assc[v2][v1] = self.proficiency(v1, v2)
                elif method == "Symmetric Proficiency":
                    assc[v1][v2] = assc[v2][v1] = self.symmetric_proficiency(v1, v2)
        return pd.DataFrame(assc).loc[self.cat_col]

    def cramers_v(self, v1, v2):
        """
        Cramer's V association
        https://en.wikipedia.org/wiki/Cramér%27s_V
        """
        if v1 == v2:
            return 1
        else:
            x, y = self.df[v1], self.df[v2]

            crosstab = pd.crosstab(x, y)
            chi2 = chi2_contingency(crosstab)[0]
            phi2 = chi2 / self.n

            r, k = crosstab.shape
            phi2_hat = max(0, phi2 - ((k - 1) * (r - 1)) / (self.n - 1))
            r_hat = r - ((r - 1) ** 2) / (self.n - 1)
            k_hat = k - ((k - 1) ** 2) / (self.n - 1)
            v_hat = np.sqrt(phi2_hat / min((k_hat - 1), (r_hat - 1)))
            return v_hat

    def proficiency(self, v1, v2):
        """
        Uncertainty coefficient / Proficiency
        https://en.wikipedia.org/wiki/Uncertainty_coefficient
        """
        if v1 == v2:
            return 1
        else:
            x, y = self.df[v1], self.df[v2]

            p_x = x.value_counts(dropna=False).values / self.n

            h_xy = self.conditional_entropy(x, y)
            h_x = entropy(p_x)

            proficiency = (h_x - h_xy) / h_x
            return proficiency

    def symmetric_proficiency(self, v1, v2):
        """
        Weighted Average between proficiency U(X|Y) and U(Y|X)
        https://en.wikipedia.org/wiki/Uncertainty_coefficient
        """
        if v1 == v2:
            return 1
        else:
            x, y = self.df[v1], self.df[v2]

            p_x = x.value_counts(dropna=False).values / self.n
            p_y = y.value_counts(dropna=False).values / self.n

            h_xy = self.conditional_entropy(x, y)
            h_yx = self.conditional_entropy(y, x)
            h_x = entropy(p_x)
            h_y = entropy(p_y)
            return 1 - (h_xy + h_yx) / (h_x + h_y)

    def conditional_entropy(self, x, y):
        """
        Wikipedia: https://en.wikipedia.org/wiki/Conditional_entropy
        """
        y_count = Counter(y)
        xy_count = Counter(list(zip(x, y)))
        entropy = sum(-xy_count[xy] * np.log(xy_count[xy] / y_count[xy[1]]) for xy in xy_count.keys())
        return entropy / self.n

