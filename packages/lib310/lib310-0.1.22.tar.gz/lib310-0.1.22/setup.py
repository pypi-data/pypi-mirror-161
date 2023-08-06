# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lib310',
 'lib310.data',
 'lib310.database',
 'lib310.database.charts',
 'lib310.machinelearning',
 'lib310.tools',
 'lib310.visualization']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.79,<2.0',
 'google-cloud-bigquery>=3.2.0,<4.0.0',
 'google-cloud>=0.34.0,<0.35.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy<1.23.0',
 'pandas>=1.4.3,<2.0.0',
 'plotly>5.4.0',
 'rich>=12.4.4,<13.0.0',
 'scanpy>=1.9.1,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'torch>=1.12.0,<2.0.0',
 'transformers>=4.20.1,<5.0.0']

setup_kwargs = {
    'name': 'lib310',
    'version': '0.1.22',
    'description': 'lib310 Python Package',
    'long_description': None,
    'author': 'Mohsen Naghipourfar',
    'author_email': 'naghipourfar@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.8,<3.11',
}


setup(**setup_kwargs)
