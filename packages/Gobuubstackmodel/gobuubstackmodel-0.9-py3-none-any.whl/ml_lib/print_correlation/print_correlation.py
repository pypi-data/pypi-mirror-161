import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def print_correlation(df: pd.DataFrame, plt_title: str) -> plt.show():

    """
        Function for print correlation matrix of a specific dataframe

        Params:
            - DataFrame -> pd.DataFrame
            - Title for the plot -> str
        Returns:
            - Lower diagonal Correlation matrix plot

    """

    correlation = df.corr()

    mask = np.zeros_like(correlation, dtype=bool)
    mask[np.triu_indices_from(mask)] = True

    f, ax = plt.subplots(figsize=(15, 15))

    plt.title(f'{plt_title} Correlation Matrix')

    colormap = sns.diverging_palette(180, 20, as_cmap=True)
    sns.heatmap(correlation, mask=mask, cmap=colormap, vmax=1, vmin =-1, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True)

    plt.savefig(f'{plt_title}_correlation_matrix.png')

    return plt.show()

