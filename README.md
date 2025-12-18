# ♟️ py4swiss

[![CI](https://github.com/Moritz72/py4swiss/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/yourrepo/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Moritz72/py4swiss/branch/main/graph/badge.svg)](https://codecov.io/gh/Moritz72/py4swiss)
[![Python 3.11](https://img.shields.io/badge/python-3.11+-blue)](https://img.shields.io/badge/python-3.11+-blue)
[![Ruff](https://img.shields.io/badge/linting-ruff-blue)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/types-mypy-blue)](https://github.com/python/mypy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*py4swiss* is a python package for pairing Swiss-system chess tournaments.

The code is heavily inspired by [bbpPairings](https://github.com/BieremaBoyzProgramming/bbpPairings)
and also directly utitlizes the maximum weight matching algorithm implemented there.

Supports Windows, Linux (Ubuntu), and macOS.

## 📄 Tournament Report File

For generation of pairings, an input file containing the entire history of the tournament up until this point is
required.
This file needs to be a **TRF(x)** as defined by the
[javafo User Manual](https://www.rrweb.org/javafo/aum/JaVaFo2_AUM.htm).

Note that unlike *javafo*, if no initial color is provided, *py4swiss* will default to `white1` instead of choosing
randomly.

## 📦 Installation

You can install this package directly from PyPI using `pip` via

```bash
pip install py4swiss
```

If you prefer, you can also install the latest version from the source repository via

```bash
git clone https://github.com/Moritz72/py4swiss.git
cd py4swiss
pip install .
```

Pre-built binary files for each supported OS are also available in the
[Releases section](https://github.com/Moritz72/py4swiss/releases).
## ️ ⚙️ Usage

To generate pairings for a given tournament, run

```bash
py4swiss -t <trf-file>
```

Additional arguments can be specified for more precise control.

| Argument         | Description                             | Default        |
|------------------|-----------------------------------------|----------------|
| `-e, --engine`   | Pairing engine                          | `dutch`        |
| `-p, --pairings` | Output file for pairings                | `pairings.txt` |

## 🧩 Variants

### FIDE Dutch System

Pairing engine: `dutch`

This variant is implements the [(Swiss) Dutch System](https://handbook.fide.com/chapter/C0403Till2026) (until 2026)
rules by FIDE.
It was tested against and produces results identical to
[bbpPairings](https://github.com/BieremaBoyzProgramming/bbpPairings).

### FIDE Dubov System

Pairing engine: `dubov`

This variant is implements the [(Swiss) Dubov System](https://handbook.fide.com/chapter/C040401202602) (from 2026)
rules by FIDE.
It was tested against and produces results identical to
[CPPDubovSystem](https://github.com/MichaelVShapiro/CPPDubovSystem) in most cases.
Note, however, that neither implementation is mature at this point in time.

## 🧪 Tests

In order to run the tests `bbpPairings.exe` needs to be in the environment.

You can download the executable from [here](https://github.com/BieremaBoyzProgramming/bbpPairings/releases/tag/v5.0.1)
and then add it to the environment via

```cmd
set PATH=%PATH%;/path/to/bbpPairings
```

for Windows or

```bash
export PATH="$PATH:/path/to/bbpPairings"
```

for Linux.

## 📜 License

This project is licensed under the [MIT License](LICENSE).
The contents of `/cpp`, however, were copied from [bbpPairings](https://github.com/BieremaBoyzProgramming/bbpPairings)
and are thus licensed under the [Apache License 2.0](licenses/Apache-2.0.txt).
