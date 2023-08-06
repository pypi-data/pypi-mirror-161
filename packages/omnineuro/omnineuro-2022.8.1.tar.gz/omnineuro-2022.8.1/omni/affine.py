"""Functions that pertain to affine matrix manipulation.
"""

import math
from typing import Tuple
import numpy as np
import nibabel as nib


def generate_rigid_transform(
    ang_x: float = 0,  # pylint: disable=dangerous-default-value
    ang_y: float = 0,
    ang_z: float = 0,
    translate: Tuple[float, float, float] = [0, 0, 0],
) -> np.ndarray:
    """Generates a rigid-body transformation.

    Parameters
    ----------
    ang_x: float
        Angle over x-axis (degrees).
    ang_y: float
        Angle over y-axis (degrees).
    ang_z: float
        Angle over z-axis (degrees).
    translate: Tuple[float, float, float]
        Length 3 tuple specifying translation (mm) for x, y, and z-axis.

    Returns
    -------
    np.ndarray
        4x4 affine matrix for given rigid-bdy transform.
    """

    def c(angle):
        return np.cos(angle * np.pi / 180)

    def s(angle):
        return np.sin(angle * np.pi / 180)

    Rx = np.array([[1, 0, 0, 0], [0, c(ang_x), -s(ang_x), 0], [0, s(ang_x), c(ang_x), 0], [0, 0, 0, 1]])
    Ry = np.array([[c(ang_y), 0, s(ang_y), 0], [0, 1, 0, 0], [-s(ang_y), 0, c(ang_y), 0], [0, 0, 0, 1]])
    Rz = np.array([[c(ang_z), -s(ang_z), 0, 0], [s(ang_z), c(ang_z), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    trans = np.array([[0, 0, 0, translate[0]], [0, 0, 0, translate[1]], [0, 0, 0, translate[2]], [0, 0, 0, 0]])
    return np.matmul(Rz, np.matmul(Ry, Rx)) + trans


def _compose_rotation(rx: float, ry: float, rz: float) -> np.ndarray:
    """Build Rotation matrix from euler angles.

    Parameters
    ----------
    rx: float
        Rotation over x-axis (radians)
    ry: float
        Rotation over y-axis (radians)
    rz: float
        Rotation over z-axis (radians)

    Returns
    -------
    np.ndarray
        3x3 rotation matrix for given rotations.
    """

    def c(angle):
        return np.cos(angle)

    def s(angle):
        return np.sin(angle)

    Rx = np.array([[1, 0, 0], [0, c(rx), -s(rx)], [0, s(rx), c(rx)]])
    Ry = np.array([[c(ry), 0, s(ry)], [0, 1, 0], [-s(ry), 0, c(ry)]])
    Rz = np.array([[c(rz), -s(rz), 0], [s(rz), c(rz), 0], [0, 0, 1]])
    return np.matmul(Rz, np.matmul(Ry, Rx))


def _decompose_rotation(R: np.ndarray) -> Tuple[float, float, float]:
    """Decompose rotation matrix into 3 euler angles.

    Parameters
    ----------
    R: np.ndarray
        3x3 rotation matrix.

    Returns
    -------
    float
        Euler angle (radians) for x-axis
    float
        Euler angle (radians) for y-axis
    float
        Euler angle (radians) for z-axis
    """
    tx = np.arctan2(R[2, 1], R[2, 2])
    ty = np.arctan2(-R[2, 0], np.sqrt(R[2, 1] ** 2 + R[2, 2] ** 2))
    tz = np.arctan2(R[1, 0], R[0, 0])
    return tx, ty, tz


def deoblique(in_img: nib.Nifti1Image, **kwargs) -> nib.Nifti1Image:
    """Load and deoblique image.

    Parameters
    ----------
    in_img: nib.Nifti1Image
        Input image to deoblique.

    Returns
    -------
    nib.Nifti1Image
        Deobliqued image.
    """
    # get affine to deoblique on
    A = in_img.affine

    # decompose affine
    T, R, Z, S = _decompose(A)

    # decompose rotation
    r = _decompose_rotation(R)

    # deoblique
    def picify(rotation):
        return [np.around(i / (np.pi / 2)) * (np.pi / 2) for i in rotation]

    newr = picify(r)
    newR = _compose_rotation(*newr)

    # compose affine
    newA = _compose(T, newR, Z, S)

    # return deobliqued image
    return nib.Nifti1Image(in_img.get_fdata(), newA, in_img.header)


def convert_affine(
    input_affine: np.ndarray,
    input_atype: str,
    output_atype: str,
    invert: bool = False,
    target: nib.Nifti1Image = None,
    source: nib.Nifti1Image = None,
) -> np.ndarray:
    """Converts input affine to output affine of another type.

    Parameters
    ----------
    input_affine: np.ndarray
        4x4 affine matrix to convert.
    input_atype: str
        Type of affine that is input (omni/afni/fsl).
    output_atype: str
        Type of affine to output (omni/afni/fsl).
    invert: bool
        Controls whether the affine should be inverted.
    target: nib.Nifti1Image
        Target image affine is transformed to
        (required for fsl conversion).
    source: nib.Nifti1Image
        Source image affine is applying transform to
        (required for fsl conversion).

    Returns
    -------
    np.ndarray
        4x4 affine matrix in output_atype format.
    """
    if target and source:
        target = nib.as_closest_canonical(target)
        source = nib.as_closest_canonical(source)

    # convert to input affine to omni affine if not already one
    if input_atype == "omni":
        omni_affine = input_affine.copy()
    elif input_atype == "afni":
        omni_affine = _afnification(input_affine.copy())
    elif input_atype == "fsl":
        if target and source:
            omni_affine = _defslification(input_affine.copy(), target, source)
        else:
            raise ValueError("fsl affine input needs target/source defined!")
    else:
        raise ValueError("Unknown input affine type provided: {}".format(input_atype))

    # if invert specified, invert the affine
    if invert:
        omni_affine = np.linalg.inv(omni_affine)

    # convert the omni affine to specified output format
    if output_atype == "omni":
        output_affine = omni_affine
    elif output_atype == "afni":
        output_affine = _afnification(omni_affine)
    elif output_atype == "fsl":
        if target and source:
            output_affine = _fslification(omni_affine, target, source)
        else:
            raise ValueError("fsl affine output needs target/source defined!")
    else:
        raise ValueError("Unknown output affine type provided: {}".format(output_atype))

    # return the output affine
    return output_affine


def afni_affine_to_rigid_body(affines: np.ndarray) -> np.ndarray:
    """Convert multiple lines of afni transforms to rigid body

    Parameters
    ----------
    affines: np.ndarray
        n x 16 matrix of affine transforms

    Returns
    -------
    np.ndarray
        n x 6 matrix of rigid body transforms
    """
    # create list to store rigid body params
    rigid_bodies = list()

    # for each affine create
    for affine in affines:
        # reshape into 4 x 4
        affine_mat = affine.reshape(4, 4)

        # decompose the matrix
        T, R, Z, S = _decompose(affine_mat)
        rots = np.array(_decompose_rotation(R))

        # reorder and redirect rotations into afni format
        # they are in degrees and z-angle is first, then x-angle, and y-angle
        rots = (-360 * rots / (2 * np.pi))[[2, 0, 1]]

        # concatenate translations and rotations
        rigid_body = np.concatenate((T, rots))

        # append to list
        rigid_bodies.append(rigid_body)

    # return the rigid body matrix
    return np.array(rigid_bodies)


def _afnification(affine: np.ndarray) -> np.ndarray:
    """Converts/deconverts affine matrix to be afni vs omni standard.

    Parameters
    ----------
    affine: np.ndarray
        Affine matrix to convert.

    Returns
    -------
    np.ndarray
        Converted affine matrix.
    """
    # decompose the affine
    T, R, Z, S = _decompose(affine)
    rx, ry, rz = _decompose_rotation(R)

    # flip the x and y translations
    T[0] = -T[0]
    T[1] = -T[1]

    # flip shears
    S[1] = -S[1]
    S[2] = -S[2]

    # flip the rotations
    rx = -rx
    ry = -ry

    # compose rotations
    R = _compose_rotation(rx, ry, rz)

    # return composed affine
    return _compose(T, R, Z, S)


def _fsl_mats(target: nib.Nifti1Image, source: nib.Nifti1Image) -> Tuple[np.ndarray, np.ndarray]:
    """Fsl pre/post transforms.

    Parameters
    ----------
    target: nib.Nifti1Image
        Image defining target space.
    source: nib.Nifti1Image
        Image defining source space.

    Returns
    -------
    np.ndarray
        Fsl pre-transform matrix.
    np.ndarray
        Fsl post-transform matrix.
    """

    # adjust for offset/orientation in target/source
    target_swp, target_spc = _fsl_aff_adapt(target)
    source_swp, source_spc = _fsl_aff_adapt(source)

    # get pre/post matrix transfroms
    pre = target.affine.dot(np.linalg.inv(target_spc).dot(np.linalg.inv(target_swp)))
    post = np.linalg.inv(source_swp).dot(source_spc.dot(np.linalg.inv(source.affine)))
    return pre, post


def _fslification(affine: np.ndarray, target: nib.Nifti1Image, source: nib.Nifti1Image) -> np.ndarray:
    """Convert omni affine to fsl affine.

    Parameters
    ----------
    affine: np.ndarray
        Omni affine to convert.
    target: nib.Nifti1Image
        Image defining target space.
    source: nib.Nifti1Image
        Image defining source space.

    Returns
    -------
    np.ndarray
        Fsl affine.
    """

    # get fsl matrices
    pre, post = _fsl_mats(target, source)

    # get fsl type matrix
    return np.linalg.inv(post.dot(affine.dot(pre)))


def _defslification(affine: np.ndarray, target: nib.Nifti1Image, source: nib.Nifti1Image) -> np.ndarray:
    """Convert fsl affine to omni affine.

    Parameters
    ----------
    affine: np.ndarray
        Fsl affine to convert.
    target: nib.Nifti1Image
        Image defining target space.
    source: nib.Nifti1Image
        Image defining source space.

    Returns
    -------
    np.ndarray
        Omni affine.
    """
    # get fsl matrices
    pre, post = _fsl_mats(target, source)

    # get omni type matrix
    return np.linalg.inv(pre.T).dot(np.linalg.inv(post).dot(np.linalg.inv(affine)).T).T


# NIBABEL CODE #


# pylint: disable=pointless-string-statement
"""
The MIT License

Copyright (c) 2009-2019 Matthew Brett <matthew.brett@gmail.com>
Copyright (c) 2010-2013 Stephan Gerhard <git@unidesign.ch>
Copyright (c) 2006-2014 Michael Hanke <michael.hanke@gmail.com>
Copyright (c) 2011 Christian Haselgrove <christian.haselgrove@umassmed.edu>
Copyright (c) 2010-2011 Jarrod Millman <jarrod.millman@gmail.com>
Copyright (c) 2011-2019 Yaroslav Halchenko <debian@onerussian.com>
Copyright (c) 2015-2019 Chris Markiewicz <effigies@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


def _fsl_aff_adapt(space: nib.Nifti1Image):
    """Adapt FSL affines.

    Calculates a matrix to convert from the original RAS image
    coordinates to FSL's internal coordinate system of transforms.
    """
    aff = space.affine
    zooms = list(_decompose(aff)[2]) + [1]
    swp = np.eye(4)
    if np.linalg.det(aff) > 0:
        swp[0, 0] = -1.0
        swp[0, 3] = (space.shape[0] - 1) * zooms[0]
    return swp, np.diag(zooms)


# NIBABEL CODE #


# TRANSFORM3D CODE #
"""
Transforms3d
============

The transforms3d package, including all examples, code snippets and attached
documentation is covered by the 2-clause BSD license.

    Copyright (c) 2009-2019, Matthew Brett and Christoph Gohlke
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    1. Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
    IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
    THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
# Caching dictionary for common shear Ns, indices
_shearers = {}
for n in range(1, 11):
    x = (n**2 + n) / 2.0
    i = n + 1
    _shearers[x] = (i, np.triu(np.ones((i, i)), 1).astype(bool))  # pylint: disable=no-member


def _striu2mat(striu):
    """Construct shear matrix from upper triangular vector
    Parameters
    ----------
    striu: array, shape (N,)
    vector giving triangle above diagonal of shear matrix.

    Returns
    -------
    SM: array, shape (N, N)
    shear matrix

    Examples
    --------
    >>> S = [0.1, 0.2, 0.3]
    >>> striu2mat(S)
    array([[1. , 0.1, 0.2],
        [0. , 1. , 0.3],
        [0. , 0. , 1. ]])
    >>> striu2mat([1])
    array([[1., 1.],
        [0., 1.]])
    >>> striu2mat([1, 2])
    Traceback (most recent call last):
    ...
    ValueError: 2 is a strange number of shear elements

    Notes
    -----
    Shear lengths are triangular numbers.
    See http://en.wikipedia.org/wiki/Triangular_number
    """
    n = len(striu)
    # cached case
    if n in _shearers:
        N, inds = _shearers[n]
    else:  # General case
        N = ((-1 + math.sqrt(8 * n + 1)) / 2.0) + 1  # n+1 th root
        if N != math.floor(N):
            raise ValueError("%d is a strange number of shear elements" % n)
        N = int(N)
        inds = np.triu(np.ones((N, N)), 1).astype(bool)  # pylint: disable=no-member
    M = np.eye(N)
    M[inds] = striu
    return M


def _compose(T, R, Z, S=None):
    """Compose translations, rotations, zooms, [shears]  to affine

    Parameters
    ----------
    T: array-like shape (N,)
        Translations, where N is usually 3 (3D case)
    R: array-like shape (N,N)
        Rotation matrix where N is usually 3 (3D case)
    Z: array-like shape (N,)
        Zooms, where N is usually 3 (3D case)
    S: array-like, shape (P,), optional
    Shear vector, such that shears fill upper triangle above
    diagonal to form shear matrix.  P is the (N-2)th Triangular
    number, which happens to be 3 for a 4x4 affine (3D case)

    Returns
    -------
    A: array, shape (N+1, N+1)
        Affine transformation matrix where N usually == 3
        (3D case)

    Examples
    --------
    >>> T = [20, 30, 40] # translations
    >>> R = [[0, -1, 0], [1, 0, 0], [0, 0, 1]] # rotation matrix
    >>> Z = [2.0, 3.0, 4.0] # zooms
    >>> A = compose(T, R, Z)
    >>> A
    array([[ 0., -3.,  0., 20.],
        [ 2.,  0.,  0., 30.],
        [ 0.,  0.,  4., 40.],
        [ 0.,  0.,  0.,  1.]])
    >>> S = np.zeros(3)
    >>> B = compose(T, R, Z, S)
    >>> np.all(A == B)
    True
    A null set
    >>> compose(np.zeros(3), np.eye(3), np.ones(3), np.zeros(3))
    array([[1., 0., 0., 0.],
        [0., 1., 0., 0.],
        [0., 0., 1., 0.],
        [0., 0., 0., 1.]])
    """
    n = len(T)
    R = np.asarray(R)
    if R.shape != (n, n):
        raise ValueError("Expecting shape (%d,%d) for rotations" % (n, n))
    A = np.eye(n + 1)
    if S is not None:
        Smat = _striu2mat(S)
        ZS = np.dot(np.diag(Z), Smat)
    else:
        ZS = np.diag(Z)
    A[:n, :n] = np.dot(R, ZS)
    A[:n, n] = T[:]
    return A


def _decompose(A):
    """Decompose homogenous affine transformation matrix `A` into parts.

    The parts are translations, rotations, zooms, shears.
    `A` can be any square matrix, but is typically shape (4,4).
    Decomposes A into ``T, R, Z, S``, such that, if A is shape (4,4)::

        Smat = np.array([[1, S[0], S[1]],
                            [0,    1, S[2]],
                            [0,    0,    1]])
        RZS = np.dot(R, np.dot(np.diag(Z), Smat))
        A = np.eye(4)
        A[:3,:3] = RZS
        A[:-1,-1] = T

    The order of transformations is therefore shears, followed by
    zooms, followed by rotations, followed by translations.
    The case above (A.shape == (4,4)) is the most common, and
    corresponds to a 3D affine, but in fact A need only be square.

    Parameters
    ----------
    A: array shape (N,N)

    Returns
    -------
    T: array, shape (N-1,)
    Translation vector
    R: array shape (N-1, N-1)
        rotation matrix
    Z: array, shape (N-1,)
    Zoom vector.  May have one negative zoom to prevent need for negative
    determinant R matrix above
    S: array, shape (P,)
    Shear vector, such that shears fill upper triangle above
    diagonal to form shear matrix.  P is the (N-2)th Triangular
    number, which happens to be 3 for a 4x4 affine.

    Examples
    --------
    >>> T = [20, 30, 40] # translations
    >>> R = [[0, -1, 0], [1, 0, 0], [0, 0, 1]] # rotation matrix
    >>> Z = [2.0, 3.0, 4.0] # zooms
    >>> S = [0.2, 0.1, 0.3] # shears
    >>> # Now we make an affine matrix
    >>> A = np.eye(4)
    >>> Smat = np.array([[1, S[0], S[1]],
    ...                  [0,    1, S[2]],
    ...                  [0,    0,    1]])
    >>> RZS = np.dot(R, np.dot(np.diag(Z), Smat))
    >>> A[:3,:3] = RZS
    >>> A[:-1,-1] = T # set translations
    >>> Tdash, Rdash, Zdash, Sdash = decompose(A)
    >>> np.allclose(T, Tdash)
    True
    >>> np.allclose(R, Rdash)
    True
    >>> np.allclose(Z, Zdash)
    True
    >>> np.allclose(S, Sdash)
    True

    Notes
    -----
    We have used a nice trick from SPM to get the shears.  Let us call the
    starting N-1 by N-1 matrix ``RZS``, because it is the composition of the
    rotations on the zooms on the shears.  The rotation matrix ``R`` must have
    the property ``np.dot(R.T, R) == np.eye(N-1)``.  Thus ``np.dot(RZS.T,
    RZS)`` will, by the transpose rules, be equal to ``np.dot((ZS).T, (ZS))``.
    Because we are doing shears with the upper right part of the matrix, that
    means that the Cholesky decomposition of ``np.dot(RZS.T, RZS)`` will give
    us our ``ZS`` matrix, from which we take the zooms from the diagonal, and
    the shear values from the off-diagonal elements.
    """
    A = np.asarray(A)
    T = A[:-1, -1]
    RZS = A[:-1, :-1]
    ZS = np.linalg.cholesky(np.dot(RZS.T, RZS)).T
    Z = np.diag(ZS).copy()
    shears = ZS / Z[:, np.newaxis]
    n = len(Z)
    S = shears[np.triu(np.ones((n, n)), 1).astype(bool)]  # pylint: disable=no-member
    R = np.dot(RZS, np.linalg.inv(ZS))
    if np.linalg.det(R) < 0:
        Z[0] *= -1
        ZS[0] *= -1
        R = np.dot(RZS, np.linalg.inv(ZS))
    return T, R, Z, S


# TRANSFORM3D CODE #
