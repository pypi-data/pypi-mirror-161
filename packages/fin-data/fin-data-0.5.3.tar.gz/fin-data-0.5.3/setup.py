# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fin_data',
 'fin_data.database',
 'fin_data.database.tests',
 'fin_data.export',
 'fin_data.export.tests',
 'fin_data.models',
 'fin_data.queries',
 'fin_data.tools',
 'fin_data.transform',
 'fin_data.transform.data']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.28,<2.0.0',
 'asyncpg>=0.25.0,<0.26.0',
 'cytoolz>=0.11.2,<0.12.0',
 'psycopg[c]>=3.0.15,<4.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'ready-logger>=0.1.0,<0.2.0',
 'sh>=1.14.2,<2.0.0']

extras_require = \
{'export': ['s3fs>=2022.5.0,<2023.0.0',
            'boto3==1.21.0',
            'pandas>=1.4.2,<2.0.0',
            'pyarrow>=8.0.0,<9.0.0']}

setup_kwargs = {
    'name': 'fin-data',
    'version': '0.5.3',
    'description': '',
    'long_description': None,
    'author': 'Dan Kelleher',
    'author_email': 'kelleherjdan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
