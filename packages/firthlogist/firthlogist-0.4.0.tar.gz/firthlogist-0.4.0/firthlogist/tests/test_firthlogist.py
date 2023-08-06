import numpy as np
import pytest
from numpy.testing import assert_allclose
from sklearn.utils.estimator_checks import parametrize_with_checks

from firthlogist import FirthLogisticRegression, load_endometrial, load_sex2


@parametrize_with_checks([FirthLogisticRegression()])
def test_estimator(estimator, check):
    return check(estimator)


@pytest.mark.parametrize(
    "loader_func, data_shape, target_shape, n_target, xname",
    [
        (load_sex2, (239, 6), (239,), (2,), ["age", "oc", "vic", "vicl", "vis", "dia"]),
        (load_endometrial, (79, 3), (79,), (2,), ["NV", "PI", "EH"]),
    ],
)
def test_loaders(loader_func, data_shape, target_shape, n_target, xname):
    X, y, feature_names = loader_func()
    assert isinstance(X, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert X.shape == data_shape
    assert y.shape == target_shape
    assert np.unique(y).shape == n_target
    assert feature_names == xname


@pytest.fixture
def endometrial():
    X, y, _ = load_endometrial()
    data = {
        "X": X,
        "y": y,
        "logistf_coef": np.array(
            [
                2.92927330,
                -0.03475175,
                -2.60416387,
            ]
        ),
        "logistf_intercept": 3.77455951,
        "logistf_ci": np.array(
            [
                [0.6097244, 7.85463171],
                [-0.1244587, 0.04045547],
                [-4.3651832, -1.23272106],
                [1.0825371, 7.20928050],
            ]
        ),
    }
    return data


@pytest.fixture
def sex2():
    # compare with logistf for logistf::sex2
    X, y, _ = load_sex2()
    data = {
        "X": X,
        "y": y,
        "logistf_coef": np.array(
            [-1.10598131, -0.06881673, 2.26887464, -2.11140817, -0.78831694, 3.09601166]
        ),
        "logistf_intercept": 0.12025405,
        "logistf_ci": np.array(
            [
                [-1.9737884, -0.30742514],
                [-0.9414363, 0.78920202],
                [1.2730216, 3.43543273],
                [-3.2608611, -1.11773495],
                [-1.6080879, 0.01518468],
                [0.7745682, 8.03029352],
                [-0.8185591, 1.07315122],
            ]
        ),
    }
    return data


@pytest.fixture
def data(request):
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize("data", ["sex2"], indirect=True)
def test_compare_to_logistf(data):
    firth = FirthLogisticRegression(fit_intercept=True)
    firth.fit(data["X"], data["y"])
    assert_allclose(firth.coef_, data["logistf_coef"], rtol=1e-05)
    assert_allclose(firth.intercept_, data["logistf_intercept"], rtol=1e-05)
    assert_allclose(firth.ci_, data["logistf_ci"], rtol=1e-05)


@pytest.fixture
def endometrial_coef_se():
    coef = np.array([2.92927330, -0.03475175, -2.60416387, 3.77455951])
    se = np.array([1.55076, 0.03958, 0.77602, 1.48869])
    return coef, se

