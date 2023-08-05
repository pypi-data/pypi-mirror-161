"""Finite difference scheme for computing TPT and augmented TPT statistics."""


import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as spsla


def generator_from_potential_2d(potential, kT, xsep, ysep):
    """Compute the generator matrix for overdamped Langevin dynamics on a 2D potential.

    Parameters
    ----------
    potential : (nx, ny) ndarray of float
        Potential energy for a 2D system.
    kT : float
        Temperature of the system, in units of energy.
    xsep, ysep : float
        Grid spacing.

    Returns
    -------
    sparse matrix of float
        Generator matrix.

    """
    # possible transitions per step
    transitions = [
        (np.s_[:-1, :], np.s_[1:, :], xsep),
        (np.s_[1:, :], np.s_[:-1, :], xsep),
        (np.s_[:, :-1], np.s_[:, 1:], ysep),
        (np.s_[:, 1:], np.s_[:, :-1], ysep),
    ]

    nx, ny = potential.shape
    ind = np.ravel_multi_index(np.ogrid[:nx, :ny], (nx, ny))
    return _make_generator(transitions, potential, kT, ind, (nx, ny))


def generator_from_potential_3d(potential, kT, xsep, ysep, zsep):
    """Compute the generator matrix for overdamped Langevin dynamics on a 3D potential.

    Parameters
    ----------
    potential : (nx, ny, nz) ndarray of float
        Potential energy for a 3D system.
    kT : float
        Temperature of the system, in units of energy.
    xsep, ysep, zsep : float
        Grid spacing.

    Returns
    -------
    sparse matrix of float
        Generator matrix.

    """
    # possible transitions per step
    transitions = [
        (np.s_[:-1, :, :], np.s_[1:, :, :], xsep),
        (np.s_[1:, :, :], np.s_[:-1, :, :], xsep),
        (np.s_[:, :-1, :], np.s_[:, 1:, :], ysep),
        (np.s_[:, 1:, :], np.s_[:, :-1, :], ysep),
        (np.s_[:, :, :-1], np.s_[:, :, 1:], zsep),
        (np.s_[:, :, 1:], np.s_[:, :, :-1], zsep),
    ]

    nx, ny, nz = potential.shape
    ind = np.ravel_multi_index(np.ogrid[:nx, :ny, :nz], (nx, ny, nz))
    return _make_generator(transitions, potential, kT, ind, (nx, ny, nz))


def _make_generator(transitions, u, kT, ind, shape):
    data = []
    row_ind = []
    col_ind = []
    p0 = np.zeros(shape)

    # transitioning to adjacent cell
    for row, col, sep in transitions:
        p = (2.0 * kT / sep**2) / (1.0 + np.exp((u[col] - u[row]) / kT))
        p0[row] -= p
        data.append(p.ravel())
        row_ind.append(ind[row].ravel())
        col_ind.append(ind[col].ravel())

    # not transitioning
    data.append(p0.ravel())
    row_ind.append(ind.ravel())
    col_ind.append(ind.ravel())

    data = np.concatenate(data)
    row_ind = np.concatenate(row_ind)
    col_ind = np.concatenate(col_ind)
    return sps.csr_matrix((data, (row_ind, col_ind)), shape=(p0.size, p0.size))


def forward_feynman_kac(generator, weights, in_domain, function, guess):
    """Solve the forward Feynman-Kac formula.

    Parameters
    ----------
    generator : (M, M) sparse matrix of float
        Generator matrix.
    weights : (M,) ndarray of float
        Change of measure to the invariant distribution for each point.
    in_domain : (M,) ndarray of bool
        Whether each point is in the domain.
    function : (M,) ndarray of float
        Function to integrate. Must be zero outside the domain.
    guess : (M,) ndarray of float
        Guess of the solution. Must obey boundary conditions.

    Returns
    -------
    (M,) ndarray of float
        Solution of the Feynman-Kac formula at each point.

    """
    weights = np.asarray(weights)
    in_domain = np.asarray(in_domain)
    function = np.where(in_domain, function, 0.0)
    guess = np.asarray(guess)

    shape = weights.shape
    assert in_domain.shape == shape
    assert function.shape == shape
    assert guess.shape == shape

    d = in_domain.ravel()
    f = function.ravel()
    g = guess.ravel()

    a = generator[d, :][:, d]
    b = -generator[d, :] @ g - f[d]
    coeffs = spsla.spsolve(a, b)
    return (g + sps.identity(len(g), format="csr")[:, d] @ coeffs).reshape(shape)


def backward_feynman_kac(generator, weights, in_domain, function, guess):
    """Solve the backward Feynman-Kac formula.

    Parameters
    ----------
    generator : (M, M) sparse matrix of float
        Generator matrix.
    weights : (M,) ndarray of float
        Change of measure to the invariant distribution for each point.
    in_domain : (M,) ndarray of bool
        Whether each point is in the domain.
    function : (M,) ndarray of float
        Function to integrate. Must be zero outside the domain.
    guess : (M,) ndarray of float
        Guess of the solution. Must obey boundary conditions.

    Returns
    -------
    (M,) ndarray of float
        Solution of the Feynman-Kac formula at each point.

    """
    pi = np.ravel(weights)
    adjoint_generator = sps.diags(1.0 / pi) @ generator.T @ sps.diags(pi)
    return forward_feynman_kac(adjoint_generator, weights, in_domain, function, guess)


def reweight(generator):
    """Compute the change of measure to the invariant distribution.

    Parameters
    ----------
    generator : (M, M) sparse matrix of float
        Generator matrix.

    Returns
    -------
    (M,) ndarray of float
        Change of measure at each point.

    """
    mask = np.full(generator.shape[0], True)
    mask[0] = False
    a = generator.T[mask, :][:, mask]
    b = -generator.T[mask, 0]
    coeffs = spsla.spsolve(a, b)
    weights = np.empty(generator.shape[0])
    weights[0] = 1.0
    weights[mask] = coeffs
    weights /= np.sum(weights)
    return weights


def rate(generator, forward_q, backward_q, weights):
    """Compute the TPT rate.

    Parameters
    ----------
    generator : (M, M) sparse matrix of float
        Generator matrix.
    forward_q : (M,) ndarray of float
        Forward committor at each point.
    backward_q : (M,) ndarray of float
        Backward committor at each point.
    weights : (M,) ndarray of float.
        Change of measure at each point.

    Returns
    -------
    float
        TPT rate.

    """
    weights = np.asarray(weights)
    forward_q = np.asarray(forward_q)
    backward_q = np.asarray(backward_q)

    shape = weights.shape
    assert forward_q.shape == shape
    assert backward_q.shape == shape

    pi_qm = (weights * backward_q).ravel()
    qp = forward_q.ravel()
    return pi_qm @ generator @ qp


def current(generator, forward_q, backward_q, weights, cv):
    """Compute the reactive current at each point.

    Parameters
    ----------
    generator : (M, M) sparse matrix of float
        Generator matrix.
    forward_q : (M,) ndarray of float
        Forward committor at each point.
    backward_q : (M,) ndarray of float
        Backward committor at each point.
    weights : (M,) ndarray of float.
        Change of measure at each point.
    cv : (M,) ndarray of float
        Collective variable at each point.

    Returns
    -------
    (M,) ndarray of float
        Reactive current at each point.

    """
    weights = np.asarray(weights)
    forward_q = np.asarray(forward_q)
    backward_q = np.asarray(backward_q)

    shape = weights.shape
    assert forward_q.shape == shape
    assert backward_q.shape == shape

    cv = np.broadcast_to(cv, shape)

    pi_qm = (weights * backward_q).ravel()
    qp = forward_q.ravel()
    h = cv.ravel()

    forward_flux = pi_qm * (generator @ (qp * h) - h * (generator @ qp))
    backward_flux = ((pi_qm * h) @ generator - (pi_qm @ generator) * h) * qp
    result = 0.5 * (forward_flux - backward_flux)
    return result.reshape(shape)


def vector_forward_feynman_kac(
    generator,
    weights,
    transitions,
    in_domain,
    function,
    guess,
    time_transitions=None,
):
    """Solve the forward Feynman-Kac formula.

    Parameters
    ----------
    generator : (n_points, n_points) sparse matrix of float
        Generator matrix.
    weights : (n_points,) ndarray of float
        Change of measure to the invariant distribution for each point.
    transitions : (n_indices, n_indices) array-like
        Possible transitions between indices. Each element `transitions[i,j]` may be a scalar or a sparse matrix of shape (n_points, n_points).
    in_domain : (n_indices, n_points) ndarray of bool
        Whether each point is in the domain.
    function : (n_indices, n_points) ndarray of float
        Function to integrate. Must be zero outside of the domain.
    guess : (n_indices, n_points) ndarray of float
        Guess for the solution. Must obey boundary conditions.
    time_transitions : (n_indices, n_indices, n_points) ndarray of float, optional
        Time-dependent transitions between indices.

    Returns
    -------
    (n_indices, n_points) ndarray of float
        Solution of the Feynman-Kac formula at each point.

    """
    pi = np.array([weights] * len(transitions))
    # time-independent term
    gen = sps.bmat(
        [[generator.multiply(mij) for mij in mi] for mi in transitions],
        format="csr",
    )
    # time-dependent term
    if time_transitions is not None:
        gen += sps.bmat(
            [[sps.diags(np.ravel(mij)) for mij in mi] for mi in time_transitions],
            format="csr",
        )
    return forward_feynman_kac(gen, pi, in_domain, function, guess)


def vector_backward_feynman_kac(
    generator,
    weights,
    transitions,
    in_domain,
    function,
    guess,
    time_transitions=None,
):
    """Solve the backward Feynman-Kac formula.

    Parameters
    ----------
    generator : (n_points, n_points) sparse matrix of float
        Generator matrix.
    weights : (n_points,) ndarray of float
        Change of measure to the invariant distribution for each point.
    transitions : (n_indices, n_indices) array-like
        Possible transitions between indices. Each element `transitions[i,j]` may be a scalar or a sparse matrix of shape (n_points, n_points).
    in_domain : (n_indices, n_points) ndarray of bool
        Whether each point is in the domain.
    function : (n_indices, n_points) ndarray of float
        Function to integrate. Must be zero outside of the domain.
    guess : (n_indices, n_points) ndarray of float
        Guess for the solution. Must obey boundary conditions.
    time_transitions : (n_indices, n_indices, n_points) ndarray of float, optional
        Time-dependent transitions between indices.

    Returns
    -------
    (n_indices, n_points) ndarray of float
        Solution of the Feynman-Kac formula at each point.

    """
    pi = np.array([weights] * len(transitions))
    # time-independent term
    gen = sps.bmat([[generator.multiply(mij) for mij in mi] for mi in transitions], format="csr")
    # time-dependent term
    if time_transitions is not None:
        gen += sps.bmat([[sps.diags(np.ravel(mij)) for mij in mi] for mi in time_transitions], format="csr")
    return backward_feynman_kac(gen, pi, in_domain, function, guess)


def pathway_rate(
    generator,
    forward_kq,
    backward_kq,
    weights,
    transitions,
    time_transitions=None,
):
    """Compute the TPT rate for a pathway.

    Parameters
    ----------
    generator : (n_points, n_points) sparse matrix of float
        Generator matrix.
    forward_kq : (n_indices, n_points) ndarray of float
        Product of q_+ and k_+ at each point.
    backward_kq : (n_indices, n_points) ndarray of float
        Product of q_- and k_- at each point.
    weights : (n_points,) ndarray of float.
        Change of measure to the invariant distribution at each point.
    transitions : (n_indices, n_indices) array-like
        Possible transitions between indices. Each element `transitions[i,j]` may be a scalar or a sparse matrix of shape (n_points, n_points).
    time_transitions : (n_indices, n_indices, n_points) ndarray of float, optional
        Time-dependent transitions between indices.

    Returns
    -------
    float
        TPT rate.

    """
    pi = np.array([weights] * len(transitions))
    # time-independent term
    gen = sps.bmat([[generator.multiply(mij) for mij in mi] for mi in transitions], format="csr")
    # time-dependent term
    if time_transitions is not None:
        gen += sps.bmat([[sps.diags(np.ravel(mij)) for mij in mi] for mi in time_transitions], format="csr")
    return rate(gen, forward_kq, backward_kq, pi)


def pathway_current(
    generator,
    forward_kq,
    backward_kq,
    weights,
    transitions,
    cv,
    time_transitions=None,
):
    """Compute the reactive current for a pathway.

    Parameters
    ----------
    generator : (n_points, n_points) sparse matrix of float
        Generator matrix.
    forward_kq : (n_indices, n_points) ndarray of float
        Product of q_+ and k_+ at each point.
    backward_kq : (n_indices, n_points) ndarray of float
        Product of q_- and k_- at each point.
    weights : (n_points,) ndarray of float.
        Change of measure to the invariant distribution at each point.
    transitions : (n_indices, n_indices) array-like
        Possible transitions between indices. Each element `transitions[i,j]` may be a scalar or a sparse matrix of shape (n_points, n_points).
    cv : (n_indices, n_points) ndarray of float
        Collective variable at each point.
    time_transitions : (n_indices, n_indices, n_points) ndarray of float, optional
        Time-dependent transitions between indices.

    Returns
    -------
    (n_indices, n_points) ndarray of float
        Reactive current at each point.

    """
    pi = np.array([weights] * len(transitions))
    # time-independent term
    gen = sps.bmat([[generator.multiply(mij) for mij in mi] for mi in transitions], format="csr")
    # time-dependent term
    if time_transitions is not None:
        gen += sps.bmat([[sps.diags(np.ravel(mij)) for mij in mi] for mi in time_transitions], format="csr")
    return current(gen, forward_kq, backward_kq, pi, cv)


def spouter(m, op, a, b):
    """Compute the outer `op` of two vectors at nonzero entries of `m`.

    Parameters
    ----------
    m : sparse matrix
        Outer `op` is calculated at nonzero entries of this matrix.
    op : callable
        Ufunc taking in two vectors and returning one vector.
    a : array-like
        First input vector, flattened if not 1D.
    b : array-like
        Second input vector, flattened if not 1D. Must be the same shape as `a`.

    Returns
    -------
    sparse matrix
        Sparse matrix `c` with entries `c[i,j] = op(a[i],b[j])` where `m[i,j]` is nonzero.

    """
    a = np.asarray(a)
    b = np.asarray(b)
    assert a.shape == b.shape
    row, col = m.nonzero()
    data = op(a.ravel()[row], b.ravel()[col])
    return sps.csr_matrix((data, (row, col)), m.shape)
