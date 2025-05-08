# qpgf/error_model.py

from collections import defaultdict
import csv
import math

# Dictionary of supported hardware platforms with basis gates and decompositions
HARDWARE_CONFIGS = {
    "EAGLE": {
        "basis": {"ECR", "ID", "RZ", "SX", "X"},
        "decompositions": {
            "H": lambda q: [("RZ", [q[0]], math.pi),
                            ("SX", [q[0]], None),
                            ("RZ", [q[0]], math.pi)],
            "Y": lambda q: [("RZ", [q[0]], math.pi / 2),
                            ("X", [q[0]], None),
                            ("RZ", [q[0]], -math.pi / 2)],
            "Z": lambda q: [("RZ", [q[0]], math.pi)],
            "S": lambda q: [("RZ", [q[0]], math.pi / 2)],
            "T": lambda q: [("RZ", [q[0]], math.pi / 4)],
            "CX": lambda q: [("ECR", q, None)],
            "RY": lambda q: [("RZ", [q[0]], math.pi / 2),
                             ("SX", [q[0]], None),
                             ("RZ", [q[0]], "theta"),
                             ("SX", [q[0]], None),
                             ("RZ", [q[0]], -math.pi / 2)],
            "U": lambda q, theta, phi, lam: [
                ("RZ", [q[0]], phi),
                ("RZ", [q[0]], math.pi / 2),
                ("SX", [q[0]], None),
                ("RZ", [q[0]], theta),
                ("SX", [q[0]], None),
                ("RZ", [q[0]], -math.pi / 2),
                ("RZ", [q[0]], lam)
            ]
        }
    },

    "HERON": {
        "basis": {"CZ", "ID", "RX", "RZ", "RZZ", "SX", "X"},
        "decompositions": {
            "H": lambda q: [("RZ", [q[0]], math.pi),
                            ("SX", [q[0]], None),
                            ("RZ", [q[0]], math.pi)],
            "Y": lambda q: [("RZ", [q[0]], math.pi / 2),
                            ("X", [q[0]], None),
                            ("RZ", [q[0]], -math.pi / 2)],
            "Z": lambda q: [("RZ", [q[0]], math.pi)],
            "S": lambda q: [("RZ", [q[0]], math.pi / 2)],
            "T": lambda q: [("RZ", [q[0]], math.pi / 4)],
            "CX": lambda q: [("CZ", q, None)],
            "RY": lambda q: [("RX", [q[0]], math.pi / 2),
                             ("RZ", [q[0]], "theta"),
                             ("RX", [q[0]], -math.pi / 2)],
            "U": lambda q, theta, phi, lam: [
                ("RZ", [q[0]], phi),
                ("RX", [q[0]], math.pi / 2),
                ("RZ", [q[0]], theta),
                ("RX", [q[0]], -math.pi / 2),
                ("RZ", [q[0]], lam)
            ]
        }
    }
}

def load_error_rates(csv_path, 
                     columns_to_gates, 
                     exclude_threshold=0.99, 
                     parse_multi_qubit_gates=None):
    """
    Load error rates from a CSV file and return averaged values per gate type.

    IBM Error Information: https://quantum.ibm.com/services/resources

    Args:
        csv_path (str): Path to the CSV file.
        columns_to_gates (dict): Mapping of CSV column names to gate names.
        exclude_threshold (float): Ignore values >= this threshold (e.g., 1.0 for 100%).
        parse_multi_qubit_gates (set or None): If a gate type requires parsing multiple targets (e.g., CZ, RZZ),
                                               this set should include those gate names.

    Returns:
        dict: Mapping from gate name to average error rate.
    """
    values = defaultdict(list)
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col, gate in columns_to_gates.items():
                if col not in row or not row[col].strip():
                    continue
                try:
                    cell = row[col].strip()
                    if parse_multi_qubit_gates and col in parse_multi_qubit_gates and (":" in cell or ";" in cell):
                        for pair in cell.split(";"):
                            if not pair.strip():
                                continue
                            parts = pair.split(":")
                            if len(parts) == 2:
                                src_dst, val = parts
                                val = float(val)
                                if val < exclude_threshold:
                                    values[gate].append(val)
                    else:
                        val = float(cell)
                        if val < exclude_threshold:
                            values[gate].append(val)
                except ValueError:
                    continue

    return {g: sum(lst) / len(lst) for g, lst in values.items() if lst}