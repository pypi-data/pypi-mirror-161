"""

This module provides a number of objects (mostly functions) useful for
embedding all functions used to compute the KKT points from the
projection of a point x0 to a quadric Q.


"""

import numpy as np

eps = pow(10, -14)


def _f(Q, mu, x0):
    """Secular function.

    Given the quadric `Q` and the `n` dimensional point `x0`,
    this function evaluates the (secular) function f.

    .. math:: f(\\mu) = \\sum_{i=1}^n \\lambda_i \\Big ( \\frac{x^0_i}{1+\\mu \\lambda_i}\\Big )^2-1

    Parameters
    ----------
    Q : Quadric instance
        The quadric onto which the point x0 has to be projected.
    mu : float
        Lagrange multiplier.
    x0 : ndarray
        1-D ndarray containing the point to be projected.

    Returns
    _______
    float
        Evaluation of f defined with Q and x0 at point mu.

    """
    _sum = 0
    for i in range(Q.dim):
        if abs(x0[i]) > eps:
            if abs(mu + 1 / Q.eig[i]) < eps:
                return -np.sign(mu) * np.inf
            else:
                _sum += Q.eig[i] * pow(x0[i]/(1+mu*Q.eig[i]), 2)

    return _sum - 1  # self.c_std = - 1 !


def _d_f(Q, mu, x0):
    """Derivative of the secular function.

    Given the quadric `Q` and the `n` dimensional point `x0`,
    this function evaluates the derivative of the (secular) function f.

    .. math:: f'(\\mu) = -2 \\sum_{i=1}^n \\frac{ (\\lambda_i x^0_i)^2}{(1+\\mu \\lambda_i)^3}

    Parameters
    ----------
    Q : Quadric instance
        The quadric onto which the point x0 has to be projected.
    mu : float
        Lagrange multiplier.
    x0 : ndarray
        1-D ndarray containing the point to be projected.
    Returns
    _______
    float
        Evaluation of f' defined with Q and x0 at point mu.

    """

    _sum = 0
    for i in range(Q.dim):
        if abs(x0[i]) > eps:
            _sum += -2 * (Q.eig[i] * x0[i])**2 / (1+mu*Q.eig[i])**3
    return _sum


def _d2_f(Q, mu, x0):
    """Second order derivative of the secular function.

    Given the quadric `Q` and the `n` dimensional point `x0`,
    this function evaluates the second derivative of the (secular) function f.

    .. math:: f''(\\mu) = 6 \\sum_{i=1}^n \\frac{ (\\lambda_i x^0_i)^2 \\lambda_i}{(1+\\mu \\lambda_i)^4}

    Parameters
    ----------
    Q : Quadric instance
        The quadric onto which the point x0 has to be projected.
    mu : float
        Lagrange multiplier.
    x0 : ndarray
        1-D ndarray containing the point to be projected.
    Returns
    _______
    float
        Evaluation of f'' defined with Q and x0 at point mu.



    """
    # Q_std and x0_std
    _sum = 0
    for i in range(Q.dim):
        if abs(x0[i]) > eps:
            _sum += 6 * (Q.eig[i]**3 * x0[i]**2) / (1+mu*Q.eig[i])**4
    return _sum


def _get_e1(Q, x0):
    """Obtain largest negative pole.

    Given the quadric `Q` and the `n` dimensional point `x0`,
    this function obtain the largest negative pole of the rational function :math:`f`
    (obtained as :math:`f(\\mu)` = `fun._f(Q, mu, x0)`).

    If no such pole exists, the function returns -inf.

    Remark that poles cancel by zeros will be omitted.

    Parameters
    ----------
    Q : Quadric instance
        The quadric onto which the point x0 has to be projected.
    x0 : ndarray
        1-D ndarray containing the point to be projected.
    Returns
    _______
    e1 : float
        Largest negative pole of f.
    """

    e1 = -np.inf
    for i, x in enumerate(x0):
        if abs(x) > eps and Q.eig[i] > eps:
            return -1/Q.eig[i]
    return e1


def _get_e2(Q, x0):
    """Obtain smallest positive pole.

    Given the quadric `Q` and the `n` dimensional point `x0`,
    this function obtain the smallest positive pole of the rational function :math:`f`
    (obtained as :math:`f(\\mu)` = `fun._f(Q, mu, x0)`).

    If no such pole exists, the function returns inf.

    Remark that poles cancel by zeros will be omitted.

    Parameters
    ----------
    Q : Quadric instance
        The quadric onto which the point x0 has to be projected.
    x0 : ndarray
        1-D ndarray containing the point to be projected.
    Returns
    -------
    e2 : float
        Smallest positive pole of f.
    """

    e2 = np.inf
    for i, _ in enumerate(x0):
        if abs(x0[-i]) > eps and Q.eig[-i] < 0:
            return -1/Q.eig[-i]
    return e2


class Fun():
    """A function class.

    The Fun class provides useful function definitions for computing
    KKT points.

    Parameters
    ----------
    Q : Quadric instance
        The nonempty quadric onto which the point x0 has to be projected.
    x0 : ndarray
        1-D ndarray containing the point to be projected.
    Attributes
    ----------
    x_std : function
        Given mu, returns the associated standardized x.
    x_not_std : function
        Given mu, returns the associated not standardized x.
    f : function
        Given mu, returns f(mu).
    d_f : function
        Derivative of f.
    d2_f : function
        Second derivative of f.
    e1 : float
        Largest negative pole of f (-np.inf if no such pole exists).
    e2 : float
        Smallest positive pole of f (np.inf if no such pole exists).
    interval : tuple of float
        Search interval for the root: (e_1, e_2).
    dist : function
        Distance function to x0_not_std.
    """

    def __init__(self, Q, x0):

        if Q.is_empty:
            raise Q.EmptyQuadric
        E = np.ones(Q.dim)

        def inv_I_lA(mu):
            return np.diag(1/(E+mu*Q.eig))  # Temporary function
        self.x_std = lambda mu: inv_I_lA(mu) @ x0
        self.x_not_std = lambda mu: Q.to_non_standardized(self.x_std(mu))

        self.f = lambda mu: _f(Q, mu, x0)
        self.d_f = lambda mu: _d_f(Q, mu, x0)
        self.d2_f = lambda mu: _d2_f(Q, mu, x0)

        self.e1 = _get_e1(Q, x0)
        self.e2 = _get_e2(Q, x0)
        self.interval = self.e1, self.e2
        x0_not_std = Q.to_non_standardized(x0)

        self.dist = lambda _x: np.linalg.norm(_x - x0_not_std)
