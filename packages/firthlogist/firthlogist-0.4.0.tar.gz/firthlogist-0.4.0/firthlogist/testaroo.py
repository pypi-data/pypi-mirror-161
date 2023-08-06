import numpy as np
from firthlogist import FirthLogisticRegression, load_sex2

if __name__ == '__main__':
    # X = np.load('../letter_img_X.npy')
    # y = np.load('../letter_img_y.npy')
    # X = np.loadtxt('datasets/sex2.csv', skiprows=1, delimiter=",")
    # y = X[:, 0]
    # X = X[:, 1:]
    # feature_names = ["age", "oc", "vic", "vicl", "vis", "dia"]

    X = np.loadtxt('datasets/endometrial.csv', skiprows=1, delimiter=",")
    y = X[:, -1]
    X = X[:, :-1]
    feature_names = ["NV", "PI", "EH"]
    # X, y, _ = load_sex2()
    fl = FirthLogisticRegression(wald=True)
    fl.fit(X, y)
    fl.summary(xname=feature_names)
    # print(fl.ci_)