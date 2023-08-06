# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['firthlogist', 'firthlogist.datasets', 'firthlogist.tests']

package_data = \
{'': ['*'],
 'firthlogist': ['.ipynb_checkpoints/*',
                 '.pytest_cache/*',
                 '.pytest_cache/v/cache/*']}

install_requires = \
['numpy>=1.22.4,<2.0.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'tabulate>=0.8.10,<0.9.0']

setup_kwargs = {
    'name': 'firthlogist',
    'version': '0.4.0',
    'description': "Python implementation of Logistic Regression with Firth's bias reduction",
    'long_description': "# firthlogist\n\n[![PyPI](https://img.shields.io/pypi/v/firthlogist.svg)](https://pypi.org/project/firthlogist/)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/firthlogist)\n[![GitHub](https://img.shields.io/github/license/jzluo/firthlogist)](https://github.com/jzluo/firthlogist/blob/master/LICENSE)\n\nA Python implementation of Logistic Regression with Firth's bias reduction.\n\n\n## Installation\n    pip install firthlogist\n\n## Usage\nfirthlogist is sklearn compatible and follows the sklearn API.\n\n```python\n>>> from firthlogist import FirthLogisticRegression, load_sex2\n>>> fl = FirthLogisticRegression()\n>>> X, y, feature_names = load_sex2()\n>>> fl.fit(X, y)\nFirthLogisticRegression()\n>>> fl.summary(xname=feature_names)\n                 coef    std err     [0.025      0.975]      p-value\n---------  ----------  ---------  ---------  ----------  -----------\nage        -1.10598     0.42366   -1.97379   -0.307427   0.00611139\noc         -0.0688167   0.443793  -0.941436   0.789202   0.826365\nvic         2.26887     0.548416   1.27304    3.43543    1.67219e-06\nvicl       -2.11141     0.543082  -3.26086   -1.11774    1.23618e-05\nvis        -0.788317    0.417368  -1.60809    0.0151846  0.0534899\ndia         3.09601     1.67501    0.774568   8.03028    0.00484687\nIntercept   0.120254    0.485542  -0.818559   1.07315    0.766584\n\nLog-Likelihood: -132.5394\nNewton-Raphson iterations: 8\n```\n\n### Parameters\n\n`max_iter`: **_int_, default=25**\n\n&emsp;The maximum number of Newton-Raphson iterations.\n\n`max_halfstep`: **_int_, default=25**\n\n&emsp;The maximum number of step-halvings in one Newton-Raphson iteration.\n\n`max_stepsize`: **_int_, default=5**\n\n&emsp;The maximum step size - for each coefficient, the step size is forced to\nbe less than max_stepsize.\n\n`pl_max_iter`: **_int_, default=100**\n\n&emsp;The maximum number of Newton-Raphson iterations for finding profile likelihood confidence intervals.\n\n`pl_max_halfstep`: **_int_, default=25**\n\n&emsp;The maximum number of step-halvings in one iteration for finding profile likelihood confidence intervals.\n\n`pl_max_stepsize`: **_int_, default=5**\n\n&emsp;The maximum step size while finding PL confidence intervals - for each coefficient, the step size is forced to\nbe less than max_stepsize.\n\n`tol`: **_float_, default=0.0001**\n\n&emsp;Convergence tolerance for stopping.\n\n`fit_intercept`: **_bool_, default=True**\n\n&emsp;Specifies if intercept should be added.\n\n`skip_pvals`: **_bool_, default=False**\n\n&emsp;If True, p-values will not be calculated. Calculating the p-values can\nbe expensive if `wald=False` since the fitting procedure is repeated for each\ncoefficient.\n\n`skip_ci`: **_bool_, default=False**\n\n&emsp;If True, confidence intervals will not be calculated. Calculating the confidence intervals via profile likelihoood is time-consuming.\n\n`alpha`: **_float_, default=0.05**\n\n&emsp;Significance level (confidence interval = 1-alpha). 0.05 as default for 95% CI.\n\n`wald`: **_bool_, default=False**\n\n&emsp;If True, uses Wald method to calculate p-values and confidence intervals.\n\n### Attributes\n`bse_`\n\n&emsp;Standard errors of the coefficients.\n\n`classes_`\n\n&emsp;A list of the class labels.\n\n`ci_`\n\n&emsp; The fitted profile likelihood confidence intervals.\n\n`coef_`\n\n&emsp;The coefficients of the features.\n\n`intercept_`\n\n&emsp;Fitted intercept. If `fit_intercept = False`, the intercept is set to zero.\n\n`loglik_`\n\n&emsp;Fitted penalized log-likelihood.\n\n`n_iter_`\n\n&emsp;Number of Newton-Raphson iterations performed.\n\n`pvals_`\n\n&emsp;p-values calculated by penalized likelihood ratio tests.\n\n## References\nFirth, D (1993). Bias reduction of maximum likelihood estimates.\n*Biometrika* 80, 27–38.\n\nHeinze G, Schemper M (2002). A solution to the problem of separation in logistic\nregression. *Statistics in Medicine* 21: 2409-2419.\n",
    'author': 'Jon Luo',
    'author_email': 'jzluo@alumni.cmu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jzluo/firthlogist',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
