# qpgf/utils.py

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister

def pgf_summary(pgf):
    """
    Compute summary statistics from a PGF.

    Args:
        pgf (np.ndarray): Probability generating function as an array.

    Returns:
        dict: Dictionary containing mean, variance, max_prob, mode, and support.
    """
    values = np.arange(len(pgf))
    mean = np.dot(values, pgf)
    variance = np.dot(values**2, pgf) - mean**2
    max_prob = np.max(pgf)
    mode = np.argmax(pgf)
    support = len(pgf) - 1 if pgf[-1] > 0 else np.nonzero(pgf)[0][-1]

    return {
        "mean": mean,
        "variance": variance,
        "max_prob": max_prob,
        "mode": mode,
        "support": support
    }

def tail_probability(pgf, threshold=0.01):
    """
    Compute the total probability mass below a threshold.

    Args:
        pgf (np.ndarray): PGF array.
        threshold (float): Values below this threshold are included in the tail.

    Returns:
        float: Total probability in the tail.
    """
    if threshold is None:
        return 0.0
    return float(np.sum(pgf[pgf < threshold]))

def print_pgf_summary(pgf, label="PGF", tail_threshold=0.01):
    """
    Print a readable summary for a PGF.

    Args:
        pgf (np.ndarray): PGF array.
        label (str): Label for identifying the PGF.
        tail_threshold (float): Probability threshold for reporting tail mass.
    """
    stats = pgf_summary(pgf)
    if tail_threshold is not None:
        stats["tail_prob"] = tail_probability(pgf, threshold=tail_threshold)
        stats["tail_threshold"] = tail_threshold
    print(f"--- {label} Summary ---")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value:.4f}")
    print()

def generate_large_test_circuit(num_qubits=20, num_layers=10, include_gates=None):
    """
    Generate a large test circuit with configurable gate types.

    Args:
        num_qubits (int): Number of qubits to include.
        num_layers (int): Number of repeated gate layers.
        include_gates (list or None): List of gate types to include (e.g., ['rx', 'cx', 't', 'u']).

    Returns:
        QuantumCircuit: Qiskit QuantumCircuit with selected gate types.
    """
    from qiskit import QuantumCircuit, QuantumRegister
    import numpy as np

    if include_gates is None:
        include_gates = ['h', 'x', 'y', 'z', 's', 't', 'rx', 'ry', 'rz', 'u', 'cx']

    qr = QuantumRegister(num_qubits, 'q')
    qc = QuantumCircuit(qr)

    for layer in range(num_layers):
        for i in range(num_qubits):
            if 'h' in include_gates and i % 4 == 0:
                qc.h(qr[i])
            if 'x' in include_gates:
                qc.x(qr[i])
            if 'y' in include_gates:
                qc.y(qr[i])
            if 'z' in include_gates:
                qc.z(qr[i])
            if 's' in include_gates:
                qc.s(qr[i])
            if 't' in include_gates:
                qc.t(qr[i])
            if 'rx' in include_gates:
                qc.rx(np.pi / 4, qr[i])
            if 'ry' in include_gates:
                qc.ry(np.pi / 4, qr[i])
            if 'rz' in include_gates:
                qc.rz(np.pi / 4, qr[i])
            if 'u' in include_gates:
                qc.u(0.5, 0.5, 0.5, qr[i])

        if 'cx' in include_gates:
            for i in range(0, num_qubits - 1, 2):
                qc.cx(qr[i], qr[i + 1])

    return qc

def vqe_h2_ansatz(theta):
    """
    Build a sample variational ansatz for H2 molecule simulation with 2 qubits.

    Args:
        theta (list of float): List of rotation angles.

    Returns:
        QuantumCircuit: Qiskit QuantumCircuit implementing the ansatz.
    """
    assert len(theta) == 6
    q = QuantumRegister(2, 'q')
    qc = QuantumCircuit(q)
    qc.ry(theta[0], q[0])
    qc.ry(theta[1], q[1])
    qc.cx(q[0], q[1])
    qc.rz(theta[2], q[0])
    qc.ry(theta[3], q[0])
    qc.rz(theta[4], q[1])
    qc.ry(theta[5], q[1])
    return qc

def sample_circuit():
    """
    Generate a sample quantum circuit with various gates.

    Returns:
        QuantumCircuit: A sample QuantumCircuit object.
    """
    qubits = QuantumRegister(3, 'q')
    circuit = QuantumCircuit(qubits)

    q0, q1, q2 = qubits
    # Apply a Hadamard gate to the first qubit
    circuit.h(q0)
    # Apply a CNOT gate with q0 as control and q1 as target
    circuit.cx(q0, q1)

    # Apply an X gate (Pauli-X) to the second qubit
    circuit.x(q1)
    # Apply a Y gate (Pauli-Y) to the third qubit
    circuit.y(q2)
    # Apply a Z gate (Pauli-Z) to the first qubit
    circuit.z(q0)

    # Apply an S gate (Phase gate) to the second qubit
    circuit.s(q1)
    # Apply a T gate (T gate) to the third qubit
    circuit.t(q2)

    # Apply an RX gate (Rotation around X-axis) to the first qubit
    circuit.rx(1.57, q0)
    # Apply an RY gate (Rotation around Y-axis) to the second qubit
    circuit.ry(1.57, q1)
    # Apply an RZ gate (Rotation around Z-axis) to the third qubit
    circuit.rz(1.57, q2)

    # Apply a U gate (Arbitrary single-qubit gate) to the first qubit
    circuit.u(0.5, 0.5, 0.5, q0)
    # Apply a CNOT gate with q1 as control and q2 as target
    circuit.cx(q1, q2)

    return circuit