# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['knockoff',
 'knockoff.command',
 'knockoff.factory',
 'knockoff.sdk',
 'knockoff.sdk.container',
 'knockoff.sdk.factory',
 'knockoff.sdk.factory.next_strategy',
 'knockoff.tempdb',
 'knockoff.utilities',
 'knockoff.utilities.date',
 'knockoff.utilities.orm',
 'knockoff.utilities.testing',
 'knockoff.writer']

package_data = \
{'': ['*']}

install_requires = \
['dependency_injector>=4.39.0,<4.40.0',
 'dotty_dict>=1.2.1',
 'faker>=3.0.1',
 'ipython>=5.9.0',
 'joblib>=0.14.1',
 'networkx>=2.2',
 'numpy>=1.16.6',
 'pandas<1.4',
 'psycopg2>=2.8.4',
 'pyaml>=19.12.0',
 'pyarrow>=0.15.1',
 's3fs>=0.2.2',
 'sqlalchemy-utils>=0.32.12',
 'testing.postgresql>=1.3.0']

extras_require = \
{'complete': ['Pyrseas>=0.9.0', 'PyMySQL>=1.0.2,<1.1.0'],
 'mysql': ['PyMySQL>=1.0.2,<1.1.0']}

entry_points = \
{'console_scripts': ['knockoff = knockoff.cli_v2:main'],
 'knockoff.cli.command': ['legacy = knockoff.cli:main',
                          'run = knockoff.command.run:main',
                          'version = knockoff.command.version:main'],
 'knockoff.factory.component.function': ['numpy.random.poisson = '
                                         'numpy.random:poisson'],
 'knockoff.factory.sink.dump_strategy': ['noop = knockoff.utilities.mixin:noop',
                                         'parquet = '
                                         'knockoff.writer.pandas:to_parquet',
                                         'sql = knockoff.writer.pandas:to_sql'],
 'knockoff.factory.source.component.load_strategy': ['autoincrement = '
                                                     'knockoff.factory.component:load_autoincrement',
                                                     'faker = '
                                                     'knockoff.factory.counterfeit:load_faker_component_generator',
                                                     'function = '
                                                     'knockoff.utilities.mixin:noop',
                                                     'knockoff = '
                                                     'knockoff.utilities.mixin:noop'],
 'knockoff.factory.source.part.load_strategy': ['cartesian-product = '
                                                'knockoff.factory.part:cartesian_product_strategy',
                                                'concat = '
                                                'knockoff.factory.part:concat_strategy',
                                                'faker = '
                                                'knockoff.factory.counterfeit:load_faker',
                                                'inline = '
                                                'knockoff.factory.part:read_part_inline',
                                                'io = '
                                                'knockoff.io:load_strategy_io',
                                                'period = '
                                                'knockoff.factory.part:generate_part_periods'],
 'knockoff.factory.source.prototype.load_strategy': ['components = '
                                                     'knockoff.factory.prototype:load_prototype_from_components',
                                                     'concat = '
                                                     'knockoff.factory.part:concat_strategy',
                                                     'io = '
                                                     'knockoff.io:load_strategy_io'],
 'knockoff.factory.source.table.load_strategy': ['io = '
                                                 'knockoff.io:load_strategy_io',
                                                 'knockoff = '
                                                 'knockoff.factory.table:load_knockoff'],
 'knockoff.io.readers': ['inline = knockoff.io:read_inline',
                         'pandas.read_csv = pandas:read_csv',
                         'pandas.read_json = pandas:read_json',
                         'pandas.read_parquet = pandas:read_parquet',
                         'read_multi_parquet = knockoff.io:read_multi_parquet',
                         'sql = knockoff.io:read_sql']}

setup_kwargs = {
    'name': 'knockoff',
    'version': '4.3.2',
    'description': 'Library for generating and bootstrapping mock data',
    'long_description': 'Knockoff Factory\n---\n[![codecov](https://codecov.io/gh/Nike-Inc/knockoff-factory/branch/master/graph/badge.svg?token=93wOmtZxIk)](https://codecov.io/gh/Nike-Inc/knockoff-factory)\n[![Test](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-test.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-test.yaml) \n[![PyPi Release](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-build.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-build.yaml) \n[![Docker Build](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/docker-build.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/docker-build.yaml)\n![License](https://img.shields.io/pypi/l/knockoff)\n![Python Versions](https://img.shields.io/pypi/pyversions/knockoff)\n![Docker Image Size](https://img.shields.io/docker/image-size/nikelab222/knockoff-factory/latest)\n![Python Wheel](https://img.shields.io/pypi/wheel/knockoff)\n\nA library for generating mock data and creating database fixtures that can be used for unit testing.\n\nTable of content\n* [Installation](#installation)\n* [Changelog](#changelog)\n* [Documentation](#documentation)\n* [Unit Tests](#unit-tests)\n* [Future Work](#Future-work)\n* [Legacy YAML Based CLI](legacy.md)\n\n# <a name="installation"></a> Installation\nFrom PyPi:\n```shell script\npip install knockoff\n\n# to install with PyMySQL \npip install knockoff[mysql]\n# Note: Other MySql DBAPI\'s can be used if installed and dialect provided in connection url\n```\n\nFrom GitHub:\n```shell script\npip install git+https://github.com/Nike-Inc/knockoff-factory#egg=knockoff\n\n# to install with PyMySQL \npip install git+https://github.com/Nike-Inc/knockoff-factory#egg=knockoff[mysql]\n# Note: Other MySql DBAPI\'s can be used if installed and dialect provided in connection url\n```\n\n\n# <a name="changelog"></a> Changelog\n\nSee the [changelog](CHANGELOG.md) for a history of notable changes to knockoff.\n\n# <a name="documentation"></a> Documentation\n\nWe are working on adding more documentation and examples!  \n\n* Knockoff SDK\n    * [KnockoffTable](notebook/KnockoffTable.ipynb)\n    * [KnockoffDB](notebook/KnockoffDB.ipynb)\n* [TempDatabaseService](notebook/TempDatabaseService.ipynb)\n* [Knockoff CLI](notebook/KnockoffCLI.ipynb)\n* Unit Testing Example: Sample App\n\n\n# <a name="unit-tests"></a> Unit Tests\n\n### Prerequisites\n* docker\n* poetry (`curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python`) \n\nSome of the unit tests depend on a database instance. Knockoff will create ephemeral databases within that instance and clean\nthem up when tests have completed. By default it will attempt to connect to an existing\ninstance at `postgresql://postgres@localhost:5432/postgres` and will\ncreate and destroy databases per test. This postgres location can\nbe overridden with the `KNOCKOFF_TEST_DB_URI` environment variable.\n\nIf no external postgres instance is available for testing, but postgresql is\ninstalled, the `TEST_USE_EXTERNAL_DB` environment variable can be set to `0`.\nThe fixtures will then rely on the `testing.postgresql` library to create\nephemeral postgres instances per fixture.\n\nIf postgres is not available, dependent tests can be disabled with the\nfollowing: `export TEST_POSTGRES_ENABLED=0`.\n\nSome tests also depend on a MySql database instance. These tests can be \ndisabled with the following: `export TEST_MYSQL_ENABLED=0`.\n\nCreate the database instance using docker:\n```bash\n# Run postgres instance \ndocker run --rm  --name pg-docker -e POSTGRES_HOST_AUTH_METHOD=trust -d -p 5432:5432  postgres:11.9\n\n# Run mysql instance\ndocker run --name mysql-docker -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -p 3306:3306 -d mysql:8.0.26\n```\n\nInstall poetry:\n```bash\n# the -E flag is so we can run the mysql unit tests with the PyMySql DBAPI\npoetry install -E mysql\n```\n\nRun unit test:\n```bash\npoetry run pytest\n```\n\n# <a name="future-work"></a> Future work\n* Further documentation and examples for SDK\n* Add yaml based configuration for SDK\n* Make extensible generic output for KnockffDB.insert (csv, parquet, etc)\n* Enable append option for KnockoffDB.insert\n* Autodiscover and populate all tables by using reflection and building dependency graph with foreign key relationships\n* Parallelize execution of dag. (e.g. https://ipython.org/ipython-doc/stable/parallel/dag_dependencies.html)\n',
    'author': 'Gregory Yu',
    'author_email': 'gregory.yu@nike.com',
    'maintainer': 'Mohamed Abdul Huq Ismail',
    'maintainer_email': 'Abdul.Ismail@nike.com',
    'url': 'https://github.com/Nike-Inc/knockoff-factory',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
