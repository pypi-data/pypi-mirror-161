import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def print_scatter(x: pd.Series, y: pd.Series, clas: pd.Series) -> plt.show():
    """
        Function for plot a custom scatter plot.

        Params:
            - x: Data for x axis -> pd.Series
            - y: Data for y axis -> pd.Series
            - clas: Data info for print the labels on plot
        Return:
            - Scatter plot
    """

    x_name = x.name
    y_name = y.name
    plt.figure(figsize=(8, 8))
    plt.title(f'{x_name} vs {y_name}')
    plt.xlabel(f'{x_name}')
    plt.ylabel(f'{y_name}')
    sns.scatterplot(x, y, hue=clas)

    plt.savefig(f'../images/{x_name}_vs_{y_name}_scatter.png')

    return plt.show()
