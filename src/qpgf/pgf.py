# qpgf/pgf.py

import numpy as np
from numpy.fft import fft, ifft
from collections import defaultdict

def next_pow_two(n):
    """
    Find the next power of two greater than or equal to n.

    Args:
        n (int): Input number.

    Returns:
        int: Next power of two greater than or equal to n.
    """
    return 1 << (n - 1).bit_length()

def build_pgf(gate_list, error_rates):
    """
    Build the probability generating function (PGF) for total gate errors using FFT-based polynomial multiplication.

    Each gate contributes either 0 or k errors, where k is the number of qubits the gate touches.

    Args:
        gate_list (list): List of (gate_name, qubit_indices, param) tuples.
        error_rates (dict): Mapping from gate name to error probability.

    Returns:
        tuple: (pgf array, mean, variance)
    """
    # Build initial PGF array
    pgf = np.array([1.0])

    for gate, qubits, _ in gate_list:
        p = error_rates.get(gate.upper(), None)
        if p is None:
            raise ValueError(f"Missing error rate for gate: {gate}")
        k = len(qubits)
        gate_pgf = np.zeros(k + 1)
        gate_pgf[0] = 1 - p
        gate_pgf[k] = p

        size = next_pow_two(len(pgf) + len(gate_pgf) - 1)
        PGF_fft = fft(pgf, size)
        GATE_fft = fft(gate_pgf, size)
        result_fft = PGF_fft * GATE_fft
        pgf = np.real_if_close(ifft(result_fft))[:len(pgf) + k]

        values = np.arange(len(pgf))
        mean = np.dot(values, pgf)
        variance = np.dot(values**2, pgf) - mean**2

    return pgf[:np.nonzero(pgf)[0][-1]+1], mean, variance # Trim trailing zeros

def build_joint_pgf(gate_list, error_rates):
    """
    Build a joint PGF tracking qubit-local errors using a tensor convolution over all gates.

    Args:
        gate_list (list): List of (gate_name, qubit_indices, param) tuples.
        error_rates (dict): Mapping from gate name to error probability.

    Returns:
        dict: Mapping from error count tuples (per qubit) to probability.
    """

    # Infer number of qubits from the maximum index
    num_qubits = 1 + max(q for _, qubits, _ in gate_list for q in qubits)
    # Start with the constant 1 polynomial
    joint = defaultdict(lambda: 0.0)
    joint[(0,) * num_qubits] = 1.0

    for gate, qubits, _ in gate_list:
        p = error_rates.get(gate.upper(), None)
        if p is None:
            raise ValueError(f"Missing error rate for gate: {gate}")

        term = defaultdict(float)
        zero = (0,) * num_qubits
        one = tuple(1 if i in qubits else 0 for i in range(num_qubits))
        term[zero] = 1 - p
        term[one] = p

        new_joint = defaultdict(float)
        for (k1, v1) in joint.items():
            for (k2, v2) in term.items():
                result = tuple(k1[i] + k2[i] for i in range(num_qubits))
                new_joint[result] += v1 * v2

        joint = new_joint

    return joint

def marginal_from_joint(joint_pgf, qubit_index):
    """
    Extract the marginal PGF for a specific qubit from the joint PGF.

    Args:
        joint_pgf (dict): Joint PGF as a dict of tuple -> probability.
        qubit_index (int): Index of the qubit to extract the marginal for.

    Returns:
        np.ndarray: PGF array for the marginal distribution of that qubit.
    """
    max_k = max(k[qubit_index] for k in joint_pgf)
    marginal = np.zeros(max_k + 1)
    for k_tuple, prob in joint_pgf.items():
        marginal[k_tuple[qubit_index]] += prob
    return marginal

def total_pgf_from_joint(joint_pgf):
    """
    Convert a joint PGF to a total error PGF by summing probabilities with the same total error count.

    Args:
        joint_pgf (dict): Joint PGF mapping error count tuples to probabilities.

    Returns:
        np.ndarray: PGF for total number of qubit-local error events.
    """
    max_total = max(sum(k) for k in joint_pgf)
    total_pgf = np.zeros(max_total + 1)
    for k_tuple, prob in joint_pgf.items():
        total_errors = sum(k_tuple)
        total_pgf[total_errors] += prob
    return total_pgf