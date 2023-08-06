# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['amora',
 'amora.cli',
 'amora.dash',
 'amora.dash.components',
 'amora.dash.components.filters',
 'amora.dash.pages',
 'amora.feature_store',
 'amora.providers',
 'amora.tests']

package_data = \
{'': ['*'], 'amora': ['target/*', 'templates/*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'SQLAlchemy[mypy]==1.4.36',
 'fsspec>=2022.5.0,<2023.0.0',
 'gcsfs>=2022.5.0,<2023.0.0',
 'humanize>=4.2.3,<5.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'networkx[all]>=2.6.3,<3.0.0',
 'numpy>=1.21.1,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'protobuf<3.20.0',
 'pytest-xdist[psutil]>=2.5.0,<3.0.0',
 'pytest>=6.2.5,<8.0.0',
 'rich>=10.13,<13.0',
 'shed>=0.9.5,<0.10.0',
 'sqlalchemy-bigquery>=1.2,<2.0',
 'sqlmodel>=0.0.4,<0.0.7',
 'sqlparse>=0.3.1,<0.5.0',
 'typer[all]>=0.4.0,<0.5.0']

extras_require = \
{'dash': ['Werkzeug==2.1.2',
          'dash[testing]==2.5.1',
          'dash-cytoscape==0.3.0',
          'dash-bootstrap-components>=1.1.0,<2.0.0',
          'Authlib>=1.0',
          'dash-ace>=0.2.1,<0.3.0'],
 'feature-store': ['feast[gcp,redis]==0.18.0',
                   'prometheus-fastapi-instrumentator>=5.8.1,<6.0.0']}

entry_points = \
{'console_scripts': ['amora = amora.cli:main'],
 'pytest11': ['amora = amora.tests.pytest_plugin']}

setup_kwargs = {
    'name': 'amora',
    'version': '0.1.11rc13',
    'description': 'Amora Data Build Tool',
    'long_description': None,
    'author': 'diogommartins',
    'author_email': 'diogo.martins@stone.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9.6,<3.10',
}


setup(**setup_kwargs)
