#!/usr/bin/env python3
"""

This module defines the class `Quadric` and some
companion functions (for plotting).

"""

import numpy as np
import scipy.sparse
import imageio
from tempfile import NamedTemporaryFile
from io import BytesIO
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


from quadproj.utils import get_project_root, get_tmp_path, get_output_path, get_tmp_gif_path
from quadproj import project

root = get_project_root()
tmp_path = get_tmp_path()
output_path = get_output_path()
tmp_gif_path = get_tmp_gif_path()

global eps_p
eps_p = pow(10, -10)
eps_dev = eps_p


class Quadric:
    """
    Quadric class.

    This class defines a quadric (or quadratic hypersurface) object.
    At the moment, we only deal with nonempty and non-cylindrical
    central quadric, that is, the quadric is nonempty,
    the matrix that defines the quadric is nonsingular,
    and b' A^{-1} b / 4 != c.

    The quadric Q is the set of points that verify:
    x' A x + b' x +c = 0.

    To ease computation and be able to project easily onto Q,
    we consider the quadric in *normal* or *standardized* form:
    x' A_std x = 1.

    Such diagonalization requires computing the eigendecomposition
    that may be expensive for large dimensions.
    Setting `is_standardized=False` reduces computation but
    implies that most function methods will be disabled.

    Since unstandardized quadrics within a sign difference:
    x' A x + b'x + c = 0 <=> x' (-A) x + (-b') x + (-c) = 0
    we change the sign when this happens.

    Please refer to the `Notes` section or the companion paper for
    further explanation.


    Attributes
    ----------
    A : ndarray
        2-D ndarray :math:`\\in \\mathbb{R}^{n \\times n}` defining the not standardized quadratic form.
    b : ndarray
        1-D ndarray :math:`\\in \\mathbb{R}^n` defining the not standardized quadratic form.
    c : float
        Independent parameter of the not standardized quadratic form.
    d : ndarray
        1-D ndarray :math:`\\in \\mathbb{R}^n` containing the not standardized quadric center.
    A_std : ndarray
        2-D ndarray :math:`\\in \\mathbb{R}^{n \\times n}` standardized `A`.
    b_std : ndarray
        1-D ndarray :math:`\\in \\mathbb{R}^n` standardized `b`.
    c_std : float
        Standardized `c`.
    d_std : ndarray
        1-D ndarray :math:`\\in \\mathbb{R}^n` standardized `d`.
    dim : float
        Quadric dimension: :math:`n`.
    gamma : float
        Parameter: :math:`\\gamma = \\sqrt{\\big |c  + \\mathbf{b}^t \\mathbf{d} + \\mathbf{d}^t \\mathbf{d} \\big |} \\in \\mathbb{R}`.
    is_empty : bool
        Whether the quadric is empty.
    is_standardized : bool
        Whether the quadric is (or will be) standardized.
    eig : ndarray
        1-D ndarray :math:`\\in \\mathbb{R^n}` containing (sorted, descending) eigenvalues of `A`.
    eig_bar : ndarray
        1-D ndarray `eig` with no repetition.
    type : {''unknown'', ''ellipse'', ''hyperbola'', ''ellipsoid'', ''one_sheet_hyperboloid'',\
        ''two_sheet_hyperboloid'', ''hyperboloid''}
        Quadric type, if `is_standardized=False` then it is `unkown`.
    V : ndarray
        2-D ndarray :math:`\\in \\mathbb{R^{n \\times n}}` containing eigenvectors of `A` associated to `eig`.
    L : ndarray
        2-D ndarray :math:`\\in \\mathbb{R^{n \\times n}}` diagonal matrix containing `eig`.
    axes : ndarray
        1-D ndarray :math:`\\in \\mathbb{R^n}` containing the axis length of the quadric.

    Notes
    -----
    Let :math:`A \\in \\mathbb{R}^{n \\times n}, \\mathbf{b} \\in \\mathbb{R}^n, c \\in \\mathbb{R}`, we
    consider quadric on the form

    .. math::  \\mathbf{y}^t A \\mathbf{y} + \\mathbf{b}^t \\mathbf{y} + c = 0

    that can be reduced (via scaling and shifting) under the form

    .. math:: \\mathbf{z}^t A \\mathbf{z} = 1

    with :math:`\\mathbf{y} = \\mathbf{z}  \\gamma + \\mathbf{d}^t`,  :math:`\\mathbf{d} = - \\frac{A^{-1}  \\mathbf{b}}{2}` and
    :math:`\\gamma = \\sqrt{\\big |c  + \\mathbf{b}^t \\mathbf{d} + \\mathbf{d}^t \\mathbf{d} \\big |} \\in \\mathbb{R}`.

    This centred quadric can then be diagonalized, i.e., rotated by using the decomposition
    :math:`A = V L V^t` where :math:`L` is diagonal matrix containing the eigenvalues
    and :math:`V` the orthonormal matrix containing the associated eigenvectors.

    It follows that :math:`\\mathbf{u}^t L \\mathbf{u} = 1` with :math:`\\mathbf{u} = V^t \\mathbf{z}`
    and therefore :math:`\\mathbf{x} = \\mathbf{d} + \\gamma  V \\mathbf{u}`.

    This gives us a **standardized** (or normalized) quadric

    .. math:: \\mathcal{Q} = \\Big \\{ \\mathbf{x} \\in \\mathbb{R}^n \\Big | \\mathbf{x}^t L \\mathbf{x} - 1 = 0  \\Big \\}

    and we have

    .. math::  \\mathbf{x}^t L \\mathbf{x} - 1  =
        \\sum_{i=1}^n \\lambda_i \\mathbf{x}^2 -1 .

    **Remark**: We sort the eigenvalues from the largest to the smallest.


    """

    class EmptyQuadric(Exception):
        """
        Python-exception-derived object raised by `quadproj.quadrics.Quadric` class.

        Raised when the quadric is empty.

        .. deprecated:: 0.046
            This may change in further releases and empty quadrics could be accepted.

        """

        def __str__(self):
            return 'Quadric appears to be empty'

    class InvalidArgument(Exception):
        """
        Python-exception-derived object raised by `quadproj.quadrics.Quadric` class.

        Raised when the constructor is called with invalid arguments.

        """

        def __init__(self, msg):
            self.msg = 'Invalid input arguments\n' + msg

        def __str__(self):
            return self.msg

    class NotStandardized(Exception):
        """
        Python-exception-derived object raised by `quadproj.quadrics.Quadric` class.

        Raised while using a method requiring a standardized quadric and the instance
        is not standardized.

        """
        def __str__(self):
            return 'Quadric is not standardized, please standardize the quadric.'

    def __init__(self, param):
        try:
            self.A = param['A']
            if not np.allclose(self.A, self.A.T):
                raise self.InvalidArgument('Matrix is not symmetric!')

            self.b = param['b']
            self.c = param['c']
        except KeyError:
            raise self.InvalidArgument('Please enter matrices (ndarray)\
                             A [n x n], b [n x 1] and a float c')
        self.d = np.linalg.solve(self.A, -self.b/2.0)
        self.dim = np.size(self.A, 0)
        if param.get('diagonalize') is not bool:
            self.is_standardized = True
        else:
            self.is_standardized = param['diagonalize']

        if self.is_standardized:
            self.eig, self.V = np.linalg.eig(self.A)
            idx = np.argsort(-self.eig)
            self.eig = self.eig[idx]
            indexes = np.unique(self.eig[idx], return_index=True)[1]
            self.eig_bar = [self.eig[_idx] for _idx in sorted(indexes)]
            # self.poles_full = -1/self.eig
            # self.poles_full_sorted = np.sort(self.poles_full)
            self.L = np.diag(self.eig)  # correctly sorted
            self.V = self.V[:, idx]
            self.standardize()
            self.axes = np.sign(self.eig) * 1/np.sqrt(abs(self.eig))
        self.set_type()

        self.gamma = self.c + self.b.T @ self.d + self.d.T @ self.A @ self.d
        if self.is_standardized:
            self.is_empty = self.check_empty()
        else:
            self.is_empty = 'unkown'
        if self.is_empty:
            print('Quadric appears to be empty!')
            # raise self.EmptyQuadric

        if self.gamma > 0:  # and self.d.T @ self.A @ self.d < 0: TODO TOREVIE
            print('\n\nSwitching equality sign!\n\n')
            param['A'] = - param['A']
            param['b'] = - param['b']
            param['c'] = - param['c']
            self.__init__(param)

        assert self.dim > 1, 'one dimensional case is not yet supported'  # TODO remove assert

    def check_empty(self):
        """
        Check whether the quadric is empty.

        This is done only if `is_standardized=True`.

        """
        if not self.is_standardized:
            raise self.NotStandardized
        if self.c_std < 0:
            p = np.sum(self.eig > 0)
        else:
            p = np.sum(self.eig < 0)
        return p == 0

    def standardize(self):
        """
        Standardize the quadric.
        """
        self.A_std = self.L
        self.b_std = np.zeros(self.dim)
        self.c_std = -1
        self.d_std = np.zeros(self.dim)
        self.is_standardized = True

    def is_feasible(self, x):
        return abs(self.evaluate_point(x)) <= eps_dev

    def evaluate_point(self, x):
        """
        Compute x' A x + b' x + c.

        Parameters
        ----------
        x : ndarray
            1-D array, point not standardized.
        """
        if scipy.sparse.issparse(self.A):
            out = np.dot(self.A.dot(x), x) + np.dot(self.b, x) + self.c
        else:
            out = np.dot(np.dot(x, self.A), x) + np.dot(self.b, x) + self.c
        return out

    def is_in_quadric(self, x):
        """
        Check whether a point is inside the quadric.

        For a circle (boundary of a 1-D ball),
        check whether it is in the ball.

        Parameters
        ----------
        x : ndarray
            1-D array, point not standardized.
        """
        return self.evaluate_point(x) <= 0

    def get_tangent_plane(self, x, forced=False):
        """
        Compute the direction of the tangent space.

        Parameters
        ----------
        x : ndarray
            1-D array, point not standardized and feasible.
        force : bool
            If `True`, compute the tangent plane even if `x` is not feasible.
        """
        if not forced:
            if not self.is_feasible(x):
                raise ValueError('Cannot compute tan gent plane on infeasible points')
        Tp = 2 * self.A @ x + self.b
        return Tp

    def set_type(self):
        """Set the quadric type.

        """
        if np.any(self.axes == 0):
            raise self.InvalidArgument('Quadric should be nondegenerated, i.e., \
                                       A should be invertible.')
        if not self.is_standardized:
            self.type = 'unknown'
        elif self.dim == 2 and np.all(self.axes > 0):
            self.type = 'ellipse'
        elif self.dim == 2 and self.axes[0]*self.axes[1] < 0:
            self.type = 'hyperbole'
        elif np.all(self.axes > 0):
            self.type = 'ellipsoid'
        elif self.dim == 3 and np.prod(self.axes) > 0:
            self.type = 'two_sheet_hyperboloid'
        elif self.dim == 3 and np.prod(self.axes) < 0:
            self.type = 'one_sheet_hyperboloid'
        else:
            self.type = 'hyperboloid'

    def to_non_standardized(self, x):
        """Unstandardize a point.

        Given a standardized point x such that
        x' L x = 1,
        returns a point y such that
        y' A y + b' y + c = 0.

        Parameters
        ----------
        x : ndarray
            1-dimensional ndarray :math:`\\in \\mathbb{R}^n` non-standardized input.
        Returns
        -------
        x : ndarray
            1-dimensional ndarray :math:`\\in \\mathbb{R}^n` standardized output.
        """

        if not self.is_standardized:
            raise self.NotStandardized()
        y = self.V @ (x * np.sqrt(abs(self.gamma))) + self.d
        return y

    def to_standardized(self, y):
        """Standardize a point.

        Given a unstandardized point y such that
        y' A y + b' y + c = 0,
        returns a point x such that
        x' L x = 1.

        Parameters
        ----------
        y : ndarray
            1-dimensional ndarray :math:`\\in \\mathbb{R}^n` standardized intput.
        Returns
        -------
        x : ndarray
            1-dimensional ndarray :math:`\\in \\mathbb{R}^n` non-standardized output
        """
        if not self.is_standardized:
            raise self.NotStandardized()
        x = self.V.T @ (y-self.d) / np.sqrt(abs(self.gamma))
        return x

    def plot(self, show=False, path_file=None, show_principal_axes=False, **kwargs):
        """Plot the (2D or 3D) standardized quadric.

        This function plot a standardized quadric in the unstandardized domain.

        If the `matplotlib.pyplot.figure` `fig` and `matplotlib.axes` `ax` is not \
        provided as argument, the function creates some.

        Parameters
        ----------
        show : bool, default=False
            Whether we show the plot.
        path_file : str, default=None
            If not `None`, save the figure at `path_file`.
        show_principal_axes : bool, default=False
            Whether we show the principal axes plot.
        **kwargs : {fig, ax}
            Additional arguments with keywords.

        Returns
        -------
        fig : matplotlib.pyplot.figure
            Figure instance where the quadric is plotted.
        ax : matplotlib.axes
            Axes instance where the quadric is plotted.
        """
        if not self.is_standardized:
            raise self.NotStandardized()
        fig, ax = get_fig_ax(self)
        if kwargs:
            if 'fig' in kwargs.keys():
                fig = kwargs['fig']
            if 'ax' in kwargs.keys():
                ax = kwargs['ax']

        dim = self.dim
        assert dim <= 3, 'Sorry, I can not represent easily > 3D spaces...'  # TODO remove assert
        assert self.type != 'unknown', 'Diagonalize is none, impossible to know quadric type'  # TODO remove assert
        m = 1000
        quadric_color = 'royalblue'
        flag_hyperboloid = np.any(self.eig < 0)

        T = np.linspace(-np.pi, np.pi, m)
        x = np.zeros_like(T)
        y = np.zeros_like(T)
        gamma = (np.sqrt(abs(self.c + self.d.T @ self.A @ self.d + self.b.T @ self.d)))
        if dim == 2:
            x = np.zeros_like(T)
            y = np.zeros_like(T)

            for i, t in enumerate(T):
                if flag_hyperboloid:
                    t = t/4  # otherwise we plot too much of the quadric...
                    v = self.d + (self.V @ np.array([self.axes[0] / np.cos(t),
                                                     -self.axes[1] * np.tan(t)])) * gamma
                    v2 = self.d + (self.V @ np.array([self.axes[0] / np.cos(t+np.pi),
                                                      -self.axes[1] * np.tan(t+np.pi)])) * gamma
                    x[i//2], y[i//2] = (v[0], v[1])
                    x[i//2 + m//2], y[i//2 + m//2] = (v2[0], v2[1])
                else:
                    v = self.d + (self.V @ np.array([self.axes[0] * np.cos(t),
                                                     self.axes[1] * np.sin(t)])) * gamma
                    #   v = np.array([self.axes[0]*np.cos(t), self.axes[1] * np.sin(t)])
                    x[i], y[i] = (v[0], v[1])
            if flag_hyperboloid:
                ax.plot(x[:m//2], y[:m//2], color=quadric_color, zorder=1,
                        label=r'$\mathcal{Q}$')
                ax.plot(x[m//2:], y[m//2:], color=quadric_color, zorder=1)
            else:
                ax.plot(x, y, color=quadric_color, label=r'$\mathcal{Q}$', zorder=1)
            ax.scatter(self.d[0], self.d[1], color=quadric_color, label=r'$\mathbf{d}$', zorder=2)
            if show_principal_axes:
                for i in range(dim):
                    x0 = np.zeros(dim)
                    x0[i] = 1
                    _, xR = project.get_KKT_point_root(self, self.to_non_standardized(x0))
                    _, xL = project.get_KKT_point_root(self, self.to_non_standardized(-x0))
                    if xR is None:
                        xR = self.to_non_standardized(x0)
                        xL = self.to_non_standardized(-x0)
                    L1 = plt.Line2D([xR[0], xL[0]], [xR[1], xL[1]], linestyle='--', color='black', zorder=1)
                    ax.add_artist(L1)
                ax.plot([0], [0], label='Principal axes', color='k', linestyle='--')
        elif dim == 3:
            m1 = 40
            m2 = 20
            ax.scatter(self.d[0], self.d[1], self.d[2],
                       color=quadric_color, label=r'$\mathbf{d}$')
            if self.type == 'one_sheet_hyperboloid':
                t, s = np.mgrid[0:2*np.pi:m1 * 1j, -1:1:m2 * 1j]
                u_x = self.axes[0] * np.cos(t) * np.sqrt(1+s**2)
                u_y = self.axes[1] * np.sin(t) * np.sqrt(1+s**2)
                u_z = self.axes[2] * s
                U_vec = np.tile(self.d, (m1*m2, 1)).T\
                    + self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                surf = ax.plot_surface(x, y, z, color=quadric_color,
                                       alpha=0.3, label=r'$\mathcal{Q}$')
                surf._facecolors2d = surf._facecolors3d
                surf._edgecolors2d = surf._edgecolors3d
                ax.plot_wireframe(x, y, z, color=quadric_color, alpha=0.7)

            elif self.type == 'two_sheet_hyperboloid':
                t, s1 = np.mgrid[0:2*np.pi:m1 * 1j, 0:np.pi/2-1:m2//2 * 1j]
                _, s2 = np.mgrid[0:2*np.pi:m1 * 1j, np.pi/2+1:np.pi:m2//2 * 1j]
                s = np.hstack((s1, s2))
                t = np.hstack((t, t))
                u_x = self.axes[0] / np.cos(s)
                u_y = self.axes[1] * np.cos(t) * np.tan(s)
                u_z = self.axes[2] * np.sin(t) * np.tan(s)

                U_vec = np.tile(self.d, (m1*m2, 1)).T \
                    + self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
                #    U_vec = np.tile(self.d, (m1*m2, 1)).T
                #   +  np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten()))
                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                x1 = x[:, :m2//2]
                y1 = y[:, :m2//2]
                z1 = z[:, :m2//2]
                x2 = x[:, m2//2:]
                y2 = y[:, m2//2:]
                z2 = z[:, m2//2:]
                surf = ax.plot_surface(x1, y1, z1, color=quadric_color,
                                       alpha=0.3, label=r'$\mathcal{Q}$')
                surf._facecolors2d = surf._facecolors3d
                surf._edgecolors2d = surf._edgecolors3d
                ax.plot_wireframe(x1, y1, z1, color=quadric_color, alpha=0.7)
                surf2 = ax.plot_surface(x2, y2, z2, color=quadric_color, alpha=0.3)
                ax.plot_wireframe(x2, y2, z2, color=quadric_color, alpha=0.7)
                surf2._facecolors2d = surf._facecolors3d
                surf2._edgecolors2d = surf._edgecolors3d
            else:
                t, s = np.mgrid[0:2*np.pi:m1 * 1j, 0:np.pi:m2 * 1j]
                u_x = self.axes[0] * np.cos(t) * np.sin(s)
                u_y = self.axes[1] * np.sin(t) * np.sin(s)
                u_z = self.axes[2] * np.cos(s)
                U_vec = np.tile(self.d, (m1*m2, 1)).T\
                    + self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
                # U_vec = np.tile(self.d, (m1*m2, 1)).T
                # +  np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten()))

                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                surf = ax.plot_surface(x, y, z, color=quadric_color, alpha=0.3,
                                       label=r'$\mathcal{Q}$')
                surf._facecolors2d = surf._facecolors3d
                surf._edgecolors2d = surf._edgecolors3d
                ax.plot_wireframe(x, y, z, color=quadric_color, alpha=0.7)
            # self.ranges = [(np.min(x), np.max(x)), (np.min(y), np.max(y)),
            # (np.min(z), np.max(z))]
            if show_principal_axes:
                for i in range(dim):
                    x0 = np.zeros(dim)
                    x0[i] = 1
                    _, xR = project.get_KKT_point_root(self, self.to_non_standardized(x0))
                    _, xL = project.get_KKT_point_root(self, self.to_non_standardized(-x0))
                    if xR is None:
                        xR = self.to_non_standardized(x0)
                        xL = self.to_non_standardized(-x0)
                    ax.plot([xR[0], xL[0]], [xR[1], xL[1]], [xR[2], xL[2]], linestyle='--', color='black', zorder=1)
                ax.plot([0], [0], [0], label='Principal axes', color='k', linestyle='--')
        plt.legend()
        if show:
            plt.show()
        if path_file is not None:
            fig.savefig(path_file)

        return fig, ax

    def get_turning_gif(self, gif_path, step=2, elev=25):
        """Create a gif.

        Plot the 3D quadric and create a rotating gif.

        Parameters
        ----------
        gif_path : str, default = ''out.gif..
            Path where the gif is written.
        elev : float, default=25
            Elevation angle.
        step : float, default=1
            Degree difference between two frames.
        """
        if self.dim != 3:
            raise self.InvalidArgument(f'Cannot create gif of quadric with dimension different\
                                       then 3. Current dim is {self.dim}.')
        fig, ax = self.plot()
        ax.grid(False)
        ax.axis('off')
        get_gif(fig, ax, gif_path=gif_path, step=step, elev=elev)


def get_gif(fig, ax, gif_path='out.gif', elev=25, step=2):
    """
        Create a rotating gif of a given figure.

        Parameters
        ----------
        fig : matplotlib.pyplot.figure
            Figure object to rotate.
        ax : matplotlib.axes
            Axes object to rotate.
        gif_path : str, default='out.gif'
            Path of the output gif.
        elev : float
            Elevation angle.
        step : float
            Degree difference between two frames.
    """
    azims = np.arange(1, 360, step)
    filenames = []
    for i, azim in enumerate(azims):
        ax.view_init(elev=elev, azim=azim)
        buf = BytesIO()
        quality_val = 90
        ext = 'png'
        fig.savefig(buf, format=ext, dpi=96, quality=quality_val)
        fp = NamedTemporaryFile()
        with open(f"{fp.name}.{ext}", 'wb') as ff:
            ff.write(buf.getvalue())
            filenames.append(f"{fp.name}.{ext}")
        buf.close()
    write_gif(filenames, gif_name=gif_path)


def get_fig_ax(Q):
    """
    Create appropriate plot objects.

    This function creates a figure and axis instance \
    taking into account the dimension of the quadric.

    Parameters
    ----------
    Q : Quadric instance
        Quadric that we want to plot.

    Returns
    -------
    fig : matplotlib.pyplot.figure
        Figure instance to plot Q.
    ax : matplotlib.axes
        Axes instance to plot W.
    """
    fig = plt.figure()
    assert Q.dim in [2, 3], 'I can only plot 2 or 3D quadrics'  # TODO: remove assert into IllegalDimension exception
    if Q.dim == 2:
        ax = fig.add_subplot()
        ax.axis('equal')
        ax.set_aspect(1)
    else:
        ax = fig.add_subplot(projection='3d')
    return fig, ax


def write_gif(filenames, gif_name='out.gif'):
    """Write a gif.

    Given a list of image paths, create and safe a gif.

    Parameters
    ----------
    filenames: list of str
        List of the image paths.
    gif_name: str
        Path where to write the gif.


    """
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(gif_name, images)  # fps=25 for projection
