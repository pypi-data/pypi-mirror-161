import pandas as pd
from tqdm import tqdm
from ml_lib.train_levels import train_levels


def train_stack_model(stack : list, X_train: pd.DataFrame, y_train: pd.Series,
                      X_validation: pd.DataFrame, y_validation: pd.Series, test: pd.DataFrame) \
                      -> (pd.DataFrame, dict):

    """
        Function for train a stacked model with n levels, receives a list of lists with the models on it, the last list
        must contain only one model
        Parameters:
            - Stack: List with lists of models to train, the last list only can contain one final model
            - X_train : pd.DataFrame with data to train the different models
            - y_train : pd.Series with the target of X_train
            - X_validation : pd.DataFrame with the data to validate the model
            - y_validation : pd.Series with the target of evaluation set
            - test : pd.DataFrame with the data for make predictions
    """

    cr = ()
    preds = ((X_train, y_train, X_validation, y_validation, test), cr)

    if len(stack[-1]) > 1:

        raise ValueError(f'Exception: the length last level of stack model must be 1 and received {len(stack[-1])}')

    for s in tqdm(stack):
        preds = train_levels(s, preds[0][0], preds[0][1], preds[0][2], preds[0][3], preds[0][4])

    return (preds[0][4], {'f1_score': preds[1][0], 'kappa': preds[1][1],
                          'Precision': preds[1][2], 'Recall': preds[1][3],
                          'Confusion matrix': preds[1][4]})