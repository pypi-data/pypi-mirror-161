from firthlogist import load_sex2, FirthLogisticRegression
import numpy as np
import pandas as pd

if __name__ == '__main__':
    # X = pd.read_csv('tests/sex2.csv')
    # y = X['case']
    # X = X.iloc[:, 1:]

    X, y, feature_names = load_sex2()
    fl = FirthLogisticRegression()
    fl.fit(X, y)
    fl.summary(feature_names)
    # fl.summary(xname=X.columns.tolist())

    # X, y = load_sex2()

