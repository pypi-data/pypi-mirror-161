# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['odd_ml',
 'odd_ml.dataset_storage',
 'odd_ml.domain',
 'odd_ml.helpers',
 'odd_ml.http',
 'odd_ml.profiler',
 'odd_ml.utils']

package_data = \
{'': ['*']}

install_requires = \
['fastparquet>=0.8.1,<0.9.0',
 'ipywidgets>=7.7.1,<8.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas-profiling>=3.2.0,<4.0.0',
 'pandas>=1.4.2,<2.0.0',
 'prettytable>=3.2.0,<4.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.27.1,<3.0.0',
 's3fs>=2022.3.0,<2023.0.0',
 's3path>=0.3.4,<0.4.0',
 'scipy>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'odd-ml',
    'version': '0.6.0',
    'description': "SDK for working with pipeline's metadata from notebooks",
    'long_description': "## **odd-ml**\nWork with  **[Open Data Discovery](https://github.com/opendatadiscovery/odd-platform)** inside your notebook.\n\n### Example\n**[Notebook example](./examples/demo.ipynb)**\n\n### What you can do using odd-ml:\n\n - [x] Get list of entities from ODD Platform\n - [x] Get detailed information about entity\n - [x] Load dataframe, if dataset stored on S3\n - [x] Get dataframe's profile\n - [x] Display embedded pages from ODD Platform UI:\n   - [x] Detailed\n   - [x] Entity structure (useful for datasets)\n   - [x] Lineage\n   - [x] Search result\n\n### Roadmap\n  - [ ] Add more filters for fetching data entities (i.e by namespace)\n  - [ ] Add more dataset's storages\n\n\n\n",
    'author': 'Open Data Discovery',
    'author_email': 'pypi@opendatadiscovery.org',
    'maintainer': 'Pavel Makarichev',
    'maintainer_email': 'vixtir90@gmail.com',
    'url': 'https://opendatadiscovery.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.12,<3.11',
}


setup(**setup_kwargs)
