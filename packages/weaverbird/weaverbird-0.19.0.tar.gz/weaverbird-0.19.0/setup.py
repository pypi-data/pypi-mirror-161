# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['weaverbird',
 'weaverbird.backends',
 'weaverbird.backends.mongo_translator',
 'weaverbird.backends.mongo_translator.steps',
 'weaverbird.backends.pandas_executor',
 'weaverbird.backends.pandas_executor.steps',
 'weaverbird.backends.pandas_executor.steps.utils',
 'weaverbird.backends.pypika_translator',
 'weaverbird.backends.pypika_translator.translators',
 'weaverbird.backends.sql_translator',
 'weaverbird.backends.sql_translator.steps',
 'weaverbird.backends.sql_translator.steps.utils',
 'weaverbird.pipeline',
 'weaverbird.pipeline.steps',
 'weaverbird.pipeline.steps.utils',
 'weaverbird.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyPika>=0.48.9,<0.49.0',
 'geopandas>=0.10.2,<0.11.0',
 'numexpr>=2.8.1,<3.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pytest-xdist>=2.5.0,<3.0.0',
 'typing_extensions>=4.2,<5.0']

extras_require = \
{':extra == "playground"': ['pandas>=1.2.5,<2.0.0'],
 'playground': ['quart>=0.17,<0.18',
                'hypercorn>=0.13,<0.14',
                'pymongo[tls,srv]>=3.12.0',
                'snowflake-connector-python[pandas]>=2.7.8,<3.0.0',
                'psycopg>=3.0.15,<4.0.0',
                'google-cloud-bigquery[pandas,bqstorage]>=3.2.0,<4.0.0',
                'toucan-connectors[awsathena]>=3.8,<4.0']}

setup_kwargs = {
    'name': 'weaverbird',
    'version': '0.19.0',
    'description': 'A visual data pipeline builder with various backends',
    'long_description': "# weaverbird python package\n\nSee [docs about purpose and usage](../docs/_docs/tech/python-package.md).\n\n## Development\n\nWe use [poetry](https://python-poetry.org/) for managing dependencies.\n\nMain commands are available through `make`:\n\n    make install # Install dependecies\n\n    make format # Fix formatting issues using black and isort\n    make lint # Execute various checks\n\n    make build # Build the project prior to publication\n    make upload # Publish on pypi\n\n    make test # Execute the test suite and produce reports\n    /!\\ To run Snowflake's e2e tests, the password needs to be exported to env variables\n    as such: export SNOWFLAKE_PASSWORD='XXXXXXXXXXX'. This password is available in lastpass (user: toucan_test)\n\n### Playground server\n\nSee `playground.py`. It provides a very simple server to test the module.\n",
    'author': 'Toucan Toco',
    'author_email': 'dev@toucantoco.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
