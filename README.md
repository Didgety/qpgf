# qpgf

**qpgf** is a Python library for modeling quantum circuit error distributions using [**Probability Generating Functions (PGFs)**](https://en.wikipedia.org/wiki/Probability-generating_function). It takes gate error rates to generate interpretable statistics about errors in circuits, either globally or per qubit.

---

### ✨ Features

- Parse OpenQASM 3.0 and extract gate operations.
- Map circuits into hardware basis sets (IBM Heron or Eagle).
- Support gate decomposition strategies (decomposed vs atomic).
- Compute global and joint PGFs of error distributions.
- Visualize error distributions using `matplotlib`.
- Load error rates from CSV files.
- Fast FFT-based computation even for large circuits.

---

### 📦 Installation

```bash
git clone https://github.com/Didgety/qpgf.git
cd qpgf
pip install -e .
```

--- 
### 📂 Project Structure

```css
qpgf/
├── src/
│   └── qpgf/                ← Library
│       ├── __init__.py
│       ├── error_model.py
│       ├── parser.py
│       ├── pgf.py
│       ├── plot.py
│       └── utils.py
├── examples/               ← Example scripts
│   ├── vqe_example.py
│   └── data/               ← Sample IBM data
│       ├── ibm_eagle.csv
│       └── ibm_heron.csv
├── LICENSE
├── README.md
└── pyproject.toml
```

--- 
### 🔗 Links

[IBM Quantum](https://quantum.ibm.com/)

[Qiskit](https://qiskit.org/)

[PGF Background (Wikipedia)](https://en.wikipedia.org/wiki/Probability-generating_function)