[![PyPI version](https://badge.fury.io/py/write-pypistat.svg)](https://badge.fury.io/py/write-pypistat)
[![CI-CD](https://github.com/veghdev/write-pypistat/actions/workflows/cicd.yml/badge.svg?branch=main)](https://github.com/veghdev/write-pypistat/actions/workflows/cicd.yml)


# About The Project

write-pypistat makes it easy to collect, filter and save pypi statistics to csv files.

# Installation

write-pypistat requires `pypistats`, `numpy` and `pandas` packages.

```sh
pip install write-pypistat
```

# Usage

```python
from writepypistat import WritePypiStat

target_package = "pypistats"
csv_dir = "stats/pypistats"
write_pypistat = WritePypiStat(package_name=target_package, outdir=csv_dir)

write_pypistat.write_pypistat(
    stat_type="system",
    start_date="2021",
    end_date="2022-03",
)

write_pypistat.date_period = "month"
write_pypistat.write_pypistat(
    stat_type="overall",
    start_date="2022-01",
    end_date="2022-04-15",
)
```

Visit our [documentation](https://veghdev.github.io/write-pypistat/) site for code reference or 
our [wiki](https://github.com/veghdev/write-pypistat/wiki/) site for a step-by-step tutorial into write-pypistat.

# Contributing

We welcome contributions to the project, visit our [contributing](https://github.com/veghdev/write-pypistat/blob/main/CONTRIBUTING.md) guide for further info.

# Contact

Join our [discussions](https://github.com/veghdev/write-pypistat/discussions) page if you have any questions or comments.

# License

Copyright © 2022.

Released under the [Apache 2.0 License](https://github.com/veghdev/write-pypistat/blob/main/LICENSE).
