# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pandas-stubs']

package_data = \
{'': ['*'],
 'pandas-stubs': ['_config/*',
                  '_libs/*',
                  '_libs/tslibs/*',
                  '_libs/window/*',
                  '_testing/*',
                  'api/*',
                  'api/extensions/*',
                  'api/indexers/*',
                  'api/types/*',
                  'arrays/*',
                  'core/*',
                  'core/arrays/*',
                  'core/arrays/sparse/*',
                  'core/computation/*',
                  'core/dtypes/*',
                  'core/groupby/*',
                  'core/indexes/*',
                  'core/ops/*',
                  'core/reshape/*',
                  'core/sparse/*',
                  'core/tools/*',
                  'core/util/*',
                  'core/window/*',
                  'errors/*',
                  'io/*',
                  'io/clipboard/*',
                  'io/excel/*',
                  'io/formats/*',
                  'io/json/*',
                  'io/sas/*',
                  'plotting/*',
                  'plotting/_matplotlib/*',
                  'tseries/*',
                  'util/*']}

install_requires = \
['types-pytz>=2022.1.1']

setup_kwargs = {
    'name': 'pandas-stubs',
    'version': '1.4.3.220801',
    'description': 'Type annotations for pandas',
    'long_description': '# pandas-stubs: Public type stubs for pandas\n\n[![PyPI Latest Release](https://img.shields.io/pypi/v/pandas-stubs.svg)](https://pypi.org/project/pandas-stubs/)\n[![Conda Latest Release](https://anaconda.org/conda-forge/pandas-stubs/badges/version.svg)](https://anaconda.org/conda-forge/pandas-stubs)\n[![Package Status](https://img.shields.io/pypi/status/pandas-stubs.svg)](https://pypi.org/project/pandas-stubs/)\n[![License](https://img.shields.io/pypi/l/pandas-stubs.svg)](https://github.com/pandas-dev/pandas-stubs/blob/main/LICENSE)\n[![Downloads](https://static.pepy.tech/personalized-badge/pandas-stubs?period=month&units=international_system&left_color=black&right_color=orange&left_text=PyPI%20downloads%20per%20month)](https://pepy.tech/project/pandas-stubs)\n[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pydata/pandas)\n[![Powered by NumFOCUS](https://img.shields.io/badge/powered%20by-NumFOCUS-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)](https://numfocus.org)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n\n## What is it?\n\nThese are public type stubs for [**pandas**](http://pandas.pydata.org/), following the\nconvention of providing stubs in a separate package, as specified in [PEP 561](https://peps.python.org/pep-0561/#stub-only-packages).  The stubs cover the most typical use cases of\npandas.  In general, these stubs are narrower than what is possibly allowed by pandas,\nbut follow a convention of suggesting best recommended practices for using pandas.\n\nThe stubs are likely incomplete in terms of covering the published API of pandas.\n\nThe stubs are tested with [mypy](http://mypy-lang.org/) and [pyright](https://github.com/microsoft/pyright#readme) and are currently shipped with the Visual Studio Code extension\n[pylance](https://github.com/microsoft/pylance-release#readme).\n\n## Usage\n\nLet’s take this example piece of code in file `round.py`\n\n```python\nimport pandas as pd\n\ndecimals = pd.DataFrame({\'TSLA\': 2, \'AMZN\': 1})\nprices = pd.DataFrame(data={\'date\': [\'2021-08-13\', \'2021-08-07\', \'2021-08-21\'],\n                            \'TSLA\': [720.13, 716.22, 731.22], \'AMZN\': [3316.50, 3200.50, 3100.23]})\nrounded_prices = prices.round(decimals=decimals)\n```\n\nMypy won\'t see any issues with that, but after installing pandas-stubs and running it again:\n\n```sh\nmypy round.py\n```\n\nwe get the following error message:\n\n```text\nround.py:6: error: Argument "decimals" to "round" of "DataFrame" has incompatible type "DataFrame"; expected "Union[int, Dict[Any, Any], Series[Any]]"  [arg-type]\nFound 1 error in 1 file (checked 1 source file)\n```\n\nAnd, if you use pyright:\n\n```sh\npyright round.py\n```\n\nyou get the following error message:\n\n```text\n round.py:6:40 - error: Argument of type "DataFrame" cannot be assigned to parameter "decimals" of type "int | Dict[Unknown, Unknown] | Series[Unknown]" in function "round"\n  \xa0\xa0Type "DataFrame" cannot be assigned to type "int | Dict[Unknown, Unknown] | Series[Unknown]"\n  \xa0\xa0\xa0\xa0"DataFrame" is incompatible with "int"\n  \xa0\xa0\xa0\xa0"DataFrame" is incompatible with "Dict[Unknown, Unknown]"\n  \xa0\xa0\xa0\xa0"DataFrame" is incompatible with "Series[Unknown]" (reportGeneralTypeIssues)\n```\n\nAnd after confirming with the [docs](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.round.html)\nwe can fix the code:\n\n```python\ndecimals = pd.Series({\'TSLA\': 2, \'AMZN\': 1})\n```\n\n## Version Numbering Convention\n\nThe version number x.y.z.yymmdd corresponds to a test done with pandas version x.y.z, with the stubs released on the date mm/yy/dd.\nIt is anticipated that the stubs will be released more frequently than pandas as the stubs are expected to evolve due to more\npublic visibility.\n\n## Where to get it\n\nThe source code is currently hosted on GitHub at: <https://github.com/pandas-dev/pandas-stubs>\n\nBinary installers for the latest released version are available at the [Python\nPackage Index (PyPI)](https://pypi.org/project/pandas-stubs) and on [conda-forge](https://conda-forge.org/).\n\n```sh\n# conda\nconda install pandas-stubs\n```\n\n```sh\n# or PyPI\npip install pandas-stubs\n```\n\n## Dependencies\n\n- [pandas: powerful Python data analysis toolkit](https://pandas.pydata.org/)\n- [typing-extensions >= 4.2.0 - supporting the latest typing extensions](https://github.com/python/typing_extensions#readme)\n\n## Installation from sources\n\n- Make sure you have `python >= 3.8` installed.\n- Install poetry\n\n```sh\n# conda\nconda install poetry\n```\n\n```sh\n# or PyPI\npip install poetry\n```\n\n- Install the project dependencies\n\n```sh\npoetry update -vvv\n```\n\n- Build and install the distribution\n\n```sh\npoetry run poe build_dist\npoetry run poe install_dist\n```\n\n## License\n\n[BSD 3](LICENSE)\n\n## Documentation\n\nDocumentation is a work-in-progress.  \n\n## Background\n\nThese stubs are the result of a strategic effort lead by the core pandas team to integrate [Microsoft type stub repository](https://github.com/microsoft/python-type-stubs)\ntogether with the [VirtusLabs pandas_stubs repository](https://github.com/VirtusLab/pandas-stubs).\n\nThese stubs were initially forked from the Microsoft project <https://github.com/microsoft/python-type-stubs> as of [this commit](https://github.com/microsoft/python-type-stubs/tree/6b800063bde687cd1846122431e2a729a9de625a).\n\nWe are indebted to Microsoft and that project for the initial set of public type stubs.  We are also grateful for the original pandas-stubs project at <https://github.com/VirtusLab/pandas-stubs> that created the framework for testing the stubs.\n\n## Getting help\n\nAsk questions and report issues on the [pandas-stubs repository](https://github.com/pandas-dev/pandas-stubs/issues).  \n\n## Discussion and Development\n\nMost development discussions take place on GitHub in the [pandas-stubs repository](https://github.com/pandas-dev/pandas-stubs/). Further, the [pandas-dev mailing list](https://mail.python.org/mailman/listinfo/pandas-dev) can also be used for specialized discussions or design issues, and a [Gitter channel](https://gitter.im/pydata/pandas) is available for quick development related questions.\n\n## Contributing to pandas-stubs\n\nAll contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.  See <https://github.com/pandas-dev/pandas-stubs/tree/main/docs/> for instructions.\n',
    'author': 'The Pandas Development Team',
    'author_email': 'pandas-dev@python.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pandas.pydata.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
