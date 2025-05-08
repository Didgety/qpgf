# qpgf/parser.py

import re
from .error_model import HARDWARE_CONFIGS

# Parse OpenQASM 3.0 into gate list
def parse_qasm(qasm_str):
    """
    Parse an OpenQASM 3.0 string and extract gate operations.

    Args:
        qasm_str (str): OpenQASM 3.0 code as a string.

    Returns:
        list of tuples: Each tuple is (gate_name, qubit_list, param) where:
            - gate_name (str): Gate name
            - qubit_list (list[int]): Indices of qubits the gate acts on
            - param (str or None): Gate parameter string (if present)
    """
    lines = qasm_str.strip().splitlines()
    gate_ops = []
    qubit_decl = re.compile(r"qubit\[(\d+)\] *([a-zA-Z_]+);")
    gate_pattern = re.compile(
        r"(\w+)(\((.*?)\))? +([a-zA-Z_]+)\[(\d+)\](?:, *([a-zA-Z_]+)\[(\d+)\])?;"
    )

    for line in lines:
        if qubit_decl.match(line):
            continue  # we don't need the number of qubits here

        m = gate_pattern.match(line)
        if m:
            gate = m.group(1).upper()
            param = m.group(3)
            q1 = int(m.group(5))
            qubits = [q1]
            if m.group(6):
                q2 = int(m.group(7))
                qubits.append(q2)
            gate_ops.append((gate, qubits, param))

    return gate_ops

def translate_to_basis(gate_ops, arch_name, decomp_mode="unit", error_rates=None):
    """
    Translate parsed gate operations into basis gates for a given architecture.

    Args:
        gate_ops (list): Parsed gates from parse_qasm.
        arch_name (str): Architecture name (e.g., 'EAGLE', 'HERON').
        decomp_mode (str): One of ['unit', 'decomp'].
        error_rates (dict or None): Dictionary of error rates to update with synthetic gate entries.

    Returns:
        (list, dict): Translated list of gate ops, and possibly updated error_rates.
    """
    if arch_name not in HARDWARE_CONFIGS:
        raise ValueError(f"Unknown architecture: {arch_name}")

    config = HARDWARE_CONFIGS[arch_name]
    basis_set = config["basis"]
    decompositions = config["decompositions"]
    translated = []

    for gate, qubits, param in gate_ops:
        if gate in basis_set:
            translated.append((gate, qubits, param))
        elif gate in decompositions:
            if gate == "U" and param:
                try:
                    theta, phi, lam = [float(x.strip()) for x in param.split(",")]
                    decomp = decompositions[gate](qubits, theta, phi, lam)
                except Exception as e:
                    raise ValueError(f"Failed to parse U gate parameters: {param}") from e
            else:
                decomp = decompositions[gate](qubits)

            if decomp_mode == "decomp":
                translated.extend(decomp)
            elif decomp_mode == "unit":
                synthetic_name = f"{gate}_DECOMP"
                if error_rates is not None:
                    product = 1.0
                    for sub_gate, _, _ in decomp:
                        sub_error = error_rates.get(sub_gate.upper(), None)
                        if sub_error is None:
                            raise ValueError(f"Missing error rate for sub-gate: {sub_gate} in decomposition of {gate}")
                        product *= (1 - sub_error)
                    effective_error = 1 - product
                    error_rates[synthetic_name] = effective_error
                translated.append((synthetic_name, qubits, None))
            else:
                raise ValueError(f"Unsupported decomposition mode: {decomp_mode}")
        else:
            raise ValueError(f"Unsupported gate: {gate}")

    return translated, error_rates