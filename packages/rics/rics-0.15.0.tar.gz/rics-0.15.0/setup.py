# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rics',
 'rics._internal_support',
 'rics._internal_support.changelog',
 'rics.mapping',
 'rics.performance',
 'rics.translation',
 'rics.translation.dio',
 'rics.translation.fetching',
 'rics.translation.offline',
 'rics.utility',
 'rics.utility.collections']

package_data = \
{'': ['*']}

install_requires = \
['click', 'pandas>=1.1']

extras_require = \
{'plotting': ['matplotlib', 'seaborn'],
 'translation': ['sqlalchemy>=1.0.0', 'toml>=0.10.2']}

entry_points = \
{'console_scripts': ['rics-perf = rics.performance.cli:_main']}

setup_kwargs = {
    'name': 'rics',
    'version': '0.15.0',
    'description': 'My personal little ML engineering library.',
    'long_description': '<div align="center">\n  <img src="https://github.com/rsundqvist/rics/raw/master/docs/logo-text.png"><br>\n</div>\n\n-----------------\n\n# rics: my personal little ML engineering library. <!-- omit in toc -->\n[![PyPI - Version](https://img.shields.io/pypi/v/rics.svg)](https://pypi.python.org/pypi/rics)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rics.svg)](https://pypi.python.org/pypi/rics)\n[![Tests](https://github.com/rsundqvist/rics/workflows/tests/badge.svg)](https://github.com/rsundqvist/rics/actions?workflow=tests)\n[![Codecov](https://codecov.io/gh/rsundqvist/rics/branch/main/graph/badge.svg)](https://codecov.io/gh/rsundqvist/rics)\n[![Read the Docs](https://readthedocs.org/projects/rics/badge/)](https://rics.readthedocs.io/)\n[![PyPI - License](https://img.shields.io/pypi/l/rics.svg)](https://pypi.python.org/pypi/rics)\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n## What is it?\n\nA **collection of utility and convenience functions** that I\'ve written and rewritten over the years, until they become\nso general that it makes sense to have them **documented and tested** for inclusion in the library. The scope is\nnaturally diverse and ranges from basic enum definitions to multivariate performance testing. More advanced features, \nlike element mapping and ID translation, is built on top of basic utilities.\n\n## Highlighted Features\n\n- Multivariate [**performance testing**][perf].\n\n- Highly configurable [**element mapping**][mapping] using a wide variety of filtering, scoring and heuristic functions.\n \n- A flexible [**ID translation suite**][translation]: Converts meaningless IDs to\n  human-readable labels. Comes with prebuilt [SQL][sql-fetcher] and \n  [file-system integration][pandas-fetcher], all of which is configurable using \n  [TOML][translator-config] files.\n\n- Various other [**utilities**][utility], ranging from [logging] to [plotting] to specialized [dict] functions.\n\n[perf]: https://rics.readthedocs.io/en/latest/_autosummary/rics.performance.html#rics.performance.run_multivariate_test\n[perf-plot]: https://rics.readthedocs.io/en/latest/_autosummary/rics.performance.html#rics.performance.plot_run\n\n[mapping]: https://rics.readthedocs.io/en/latest/_autosummary/rics.mapping.html\n\n[translation]: https://rics.readthedocs.io/en/latest/_autosummary/rics.translation.html\n[sql-fetcher]: https://rics.readthedocs.io/en/latest/_autosummary/rics.translation.fetching.html#rics.translation.fetching.SqlFetcher\n[pandas-fetcher]: https://rics.readthedocs.io/en/latest/_autosummary/rics.translation.fetching.html#rics.translation.fetching.PandasFetcher\n[translator-config]: https://rics.readthedocs.io/en/latest/documentation/translator-config.html\n\n[utility]: https://rics.readthedocs.io/en/latest/_autosummary/rics.utility.html\n[logging]: https://rics.readthedocs.io/en/latest/_autosummary/rics.utility.logs.html\n[plotting]: https://rics.readthedocs.io/en/latest/_autosummary/rics.utility.plotting.html\n[dict]: https://rics.readthedocs.io/en/latest/_autosummary/rics.utility.collections.dicts.html\n\n\n## Installation\nThe package is published through the [Python Package Index (PyPI)]. Source code\nis available on GitHub: https://github.com/rsundqvist/rics\n\n```sh\npip install -U rics\n```\n\nThis is the preferred method to install ``rics``, as it will always install the\nmost recent stable release.\n\nIf you don\'t have [pip] installed, this [Python installation guide] can guide\nyou through the process.\n\n## License\n[MIT](LICENSE.md)\n\n## Documentation\nHosted on Read the Docs: https://rics.readthedocs.io\n\n## Contributing\n\nAll contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome. To get \nstarted, see the [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).\n\n[Python Package Index (PyPI)]: https://pypi.org/project/rics\n[pip]: https://pip.pypa.io\n[Python installation guide]: http://docs.python-guide.org/en/latest/starting/installation/\n',
    'author': 'Richard Sundqvist',
    'author_email': 'richard.sundqvist@live.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rsundqvist/rics',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
