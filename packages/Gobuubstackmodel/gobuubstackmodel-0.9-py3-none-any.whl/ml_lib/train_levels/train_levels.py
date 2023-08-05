import pandas as pd
from tqdm import tqdm
from sklearn.metrics import f1_score, confusion_matrix, cohen_kappa_score,\
                            precision_score, recall_score


def train_levels_models(models: list, X_train:pd.DataFrame, y_train: pd.Series,
                        X_validation:pd.DataFrame, y_validation: pd.Series, test: pd.DataFrame)\
                        -> ((pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame), tuple):
    """
        Function that train a list of models make predictions of train and test and returns an array with it

        Parameters.
            - Models : List with models to train
            - X_train : pd.DataFrame with train data
            - y_train : pd.Series with the target of train
            - X_test : pd.DataFrame with test data
            - y_test: pd.Series with the target of test

        Returns:
            - Tuple of (pd.DataFrames with the predictions of train, validation and test , y_train and y validation)
              and a custom classification report with f1_score, cohen kappa score, precision score, recall score and
              confusion matrix
    """

    preds_train = pd.DataFrame()
    preds_validation = pd.DataFrame()
    preds_test = pd.DataFrame()

    for model in tqdm(models):
        name = str(model)[:14]
        if 'cat' in name:
            name = 'catboost'
        print(f'Training {name}')
        model.fit(X_train, y_train)
        pred_train = model.predict(X_train)
        f1_train = f1_score(y_train, pred_train, average='macro')

        if f1_train > 0.96:

            print(f'f1_score on train of {name}: {f1_train}\n')
            preds_train[f'{name}'] = pred_train
            pred_val = model.predict(X_validation)
            f1_test = f1_score(y_validation, pred_val, average='macro')
            kappa = cohen_kappa_score(y_validation, pred_val)
            prec = precision_score(y_validation, pred_val)
            recall = recall_score(y_validation, pred_val)
            cm = confusion_matrix(y_validation, pred_val)
            print(f'f1_score on validation of {name}: {f1_test}')
            preds_validation[f'{name}'] = pred_val
            pred_test = model.predict(test)
            preds_test[f'{name}'] = pred_test

    return (preds_train, y_train, preds_validation, y_validation, preds_test), (f1_test, kappa, prec, recall, cm)
