# py4swiss

[![CI](https://github.com/Moritz72/py4swiss/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/yourrepo/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Moritz72/py4swiss/branch/main/graph/badge.svg)](https://codecov.io/gh/Moritz72/py4swiss)
[![Ruff](https://img.shields.io/badge/linting-ruff-blue)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/types-mypy-blue)](https://github.com/python/mypy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*py4swiss* is a pairing engine for chess tournaments
using the [(Swiss) Dutch System](https://handbook.fide.com/chapter/C0403Till2026).

The code is heavily inspired by [bbpPairings](https://github.com/BieremaBoyzProgramming/bbpPairings)
and also directly utitlizes the maximum weight matching algorithm implemented in there.

## Tests

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


## License

This project is licensed under the [MIT License](LICENSE).
The contents of `/cpp`, however, were copied from [bbpPairings](https://github.com/BieremaBoyzProgramming/bbpPairings)
and are thus licensed under the [Apache License 2.0](licenses/Apache-2.0.txt).
