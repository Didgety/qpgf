import sys
import os
import matplotlib.pyplot as plt

# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
# sys.path.insert(0, REPO_ROOT)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Example: Run PGF model on the H2 ansatz circuit
# This example demonstrates how to use the qpgf library to analyze a quantum circuit

from qpgf.parser import parse_qasm, translate_to_basis
from qpgf.error_model import load_error_rates
from qpgf.pgf import build_pgf
from qpgf.utils import print_pgf_summary, vqe_h2_ansatz
from qpgf.plot import plot_pgf

from qiskit.qasm3 import dumps

# Create a test circuit
theta = [0.1, -0.2, 0.3, 0.4, -0.5, 0.6]
circuit = vqe_h2_ansatz(theta)

# Parse QASM
qasm_str = dumps(circuit)
gate_ops = parse_qasm(qasm_str)

# Load error rates from a cleaned CSV (you must provide this)
columns_to_gates = {
    "ID": "ID", "RX": "RX", "RZ": "RZ", "SX": "SX", "X": "X", "CZ": "CZ", "RZZ": "RZZ"
}
parse_multi = {"CZ", "RZZ"}
error_rates = load_error_rates(
    "examples/data/ibm_heron.csv",
    columns_to_gates=columns_to_gates,
    exclude_threshold=0.99,
    parse_multi_qubit_gates=parse_multi
)

# Translate to hardware basis and compute PGF
translated, updated_rates = translate_to_basis(
    gate_ops, arch_name="HERON", decomp_mode="decomp", error_rates=error_rates.copy()
)

pgf, mean, var = build_pgf(translated, updated_rates)

# Plot and summarize
print_pgf_summary(pgf, label="VQE PGF")

print("Plotting if in a supported environment...")
plot_pgf(pgf, title="Decomposed Error Distribution (PGF)", threshold=0, scale='log')
plt.show()