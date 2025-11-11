# py4swiss

`py4swiss` is a pairing engine for chess tournaments
using the [(Swiss) Dutch System](https://handbook.fide.com/chapter/C0403Till2026).

The code is heavily inspired by [bbpPairings](https://github.com/BieremaBoyzProgramming/bbpPairings)
and also directly utitlizes the maximum weight matching algorithm implemented in there.

This is a work in progress.

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
and is thus licensed under the [Apache License 2.0](licenses/Apache-2.0.txt).
