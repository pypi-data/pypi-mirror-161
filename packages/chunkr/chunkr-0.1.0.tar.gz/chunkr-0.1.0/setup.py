# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['chunkr']
install_requires = \
['fsspec>=2022.7.1,<2023.0.0',
 'pandas>=1.3.5,<2.0.0',
 'paramiko>=2.11.0,<3.0.0',
 'pyarrow>=8.0.0,<9.0.0']

setup_kwargs = {
    'name': 'chunkr',
    'version': '0.1.0',
    'description': 'A library for chunking different types of data files.',
    'long_description': '# chunkr\n[![PyPI version][pypi-image]][pypi-url]\n<!-- [![Build status][build-image]][build-url] -->\n<!-- [![Code coverage][coverage-image]][coverage-url] -->\n[![GitHub stars][stars-image]][stars-url]\n[![Support Python versions][versions-image]][versions-url]\n\n\nA library for chunking different types of data files.\n\n## Getting started\n\n```bash\npip install chunkr\n```\n\n## Usage\n\nSuppose you want to chunk a csv file of 1 million records into 10 pieces, you can do this\n\n```py\nfrom chunkr import create_chunks_dir\nimport pandas as pd\n\nwith create_chunks_dir(\n            \'csv\',\n            \'csv_test\',\n            \'path/to/file\',\n            \'temp/output\',\n            100_000,\n            None,\n            None,\n            quote_char=\'"\',\n            delimiter=\',\',\n            escape_char=\'\\\\\',\n    ) as chunks_dir:\n\n        assert 1_000_000 == sum(\n            len(pd.read_parquet(file)) for file in chunks_dir.iterdir()\n        )\n\n```\n\n\n<!-- Badges -->\n\n[pypi-image]: https://img.shields.io/pypi/v/chunkr\n[pypi-url]: https://pypi.org/project/chunkr/\n[build-image]: https://github.com/1b5d/chunkr/actions/workflows/build.yaml/badge.svg\n[build-url]: https://github.com/1b5d/chunkr/actions/workflows/build.yaml\n[coverage-image]: https://codecov.io/gh/1b5d/chunkr/branch/main/graph/badge.svg\n[coverage-url]: https://codecov.io/gh/1b5d/chunkr/\n[stars-image]: https://img.shields.io/github/stars/1b5d/chunkr\n[stars-url]: https://github.com/1b5d/chunkr\n[versions-image]: https://img.shields.io/pypi/pyversions/chunkr\n[versions-url]: https://pypi.org/project/chunkr/\n',
    'author': '1b5d',
    'author_email': '8110504+1b5d@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/1b5d/chunkr',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
