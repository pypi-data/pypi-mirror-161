# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['duckdb_engine', 'duckdb_engine.tests']

package_data = \
{'': ['*']}

install_requires = \
['duckdb>=0.2.8', 'sqlalchemy>=1.3.19,<2.0.0']

extras_require = \
{':python_version == "3.6"': ['numpy>=1.19.5'],
 ':python_version >= "3.7"': ['numpy>=1.20.0']}

entry_points = \
{'sqlalchemy.dialects': ['duckdb = duckdb_engine:Dialect']}

setup_kwargs = {
    'name': 'duckdb-engine',
    'version': '0.3.0',
    'description': '',
    'long_description': '# duckdb_engine\n\n[![Supported Python Versions](https://img.shields.io/pypi/pyversions/duckdb-engine)](https://pypi.org/project/duckdb-engine/) [![PyPI version](https://badge.fury.io/py/duckdb-engine.svg)](https://badge.fury.io/py/duckdb-engine)\n\nBasic sqlalchemy driver for [DuckDB](https://duckdb.org/)\n\n## Installation\n```sh\n$ pip install duckdb-engine\n```\n\nDuckDB Engine also has a conda feedstock available, the instructions for the use of which are available in it\'s [repository](https://github.com/conda-forge/duckdb-engine-feedstock).\n\n## Usage\n\nOnce you\'ve installed this package, you should be able to just use it, as sqlalchemy does a python path search\n\n```python\nfrom sqlalchemy import Column, Integer, Sequence, String, create_engine\nfrom sqlalchemy.ext.declarative import declarative_base\nfrom sqlalchemy.orm.session import Session\n\nBase = declarative_base()\n\n\nclass FakeModel(Base):  # type: ignore\n    __tablename__ = "fake"\n\n    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)\n    name = Column(String)\n\n\neng = create_engine("duckdb:///:memory:")\nBase.metadata.create_all(eng)\nsession = Session(bind=eng)\n\nsession.add(FakeModel(name="Frank"))\nsession.commit()\n\nfrank = session.query(FakeModel).one()\n\nassert frank.name == "Frank"\n```\n\n## How to register a pandas DataFrame\n\n```python\neng = create_engine("duckdb:///:memory:")\neng.execute("register", ("dataframe_name", pd.DataFrame(...)))\n\neng.execute("select * from dataframe_name")\n```\n\n## Things to keep in mind\nDuckdb\'s SQL parser is based on the PostgreSQL parser, but not all features in PostgreSQL are supported in duckdb. Because the `duckdb_engine` dialect is derived from the `postgresql` dialect, `sqlalchemy` may try to use PostgreSQL-only features. Below are some caveats to look out for.\n\n### Auto-incrementing ID columns\nWhen defining an Integer column as a primary key, `sqlalchemy` uses the `SERIAL` datatype for PostgreSQL. Duckdb does not yet support this datatype because it\'s a non-standard PostgreSQL legacy type, so a workaround is to use the `sqlalchemy.Sequence()` object to auto-increment the key. For more information on sequences, you can find the [`sqlalchemy Sequence` documentation here](https://docs.sqlalchemy.org/en/14/core/defaults.html#associating-a-sequence-as-the-server-side-default).\n\nThe following example demonstrates how to create an auto-incrementing ID column for a simple table:\n\n```python\n>>> import sqlalchemy\n>>> engine = sqlalchemy.create_engine(\'duckdb:////path/to/duck.db\')\n>>> metadata = sqlalchemy.MetaData(engine)\n>>> user_id_seq = sqlalchemy.Sequence(\'user_id_seq\')\n>>> users_table = sqlalchemy.Table(\n...     \'users\',\n...     metadata,\n...     sqlalchemy.Column(\n...         \'id\',\n...         sqlalchemy.Integer,\n...         user_id_seq,\n...         server_default=user_id_seq.next_value(),\n...         primary_key=True,\n...     ),\n... )\n>>> metadata.create_all(bind=engine)\n```\n\n### Pandas `read_sql()` chunksize\nThe `pandas.read_sql()` method can read tables from `duckdb_engine` into DataFrames, but the `sqlalchemy.engine.result.ResultProxy` trips up when `fetchmany()` is called. Therefore, for now `chunksize=None` (default) is necessary when reading duckdb tables into DataFrames. For example:\n\n```python\n>>> import pandas as pd\n>>> import sqlalchemy\n>>> engine = sqlalchemy.create_engine(\'duckdb:////path/to/duck.db\')\n>>> df = pd.read_sql(\'users\', engine)                ### Works as expected\n>>> df = pd.read_sql(\'users\', engine, chunksize=25)  ### Throws an exception\n```\n\n## The name\n\nYes, I\'m aware this package should be named `duckdb-driver` or something, I wasn\'t thinking when I named it and it\'s too hard to change the name now\n',
    'author': 'Elliana',
    'author_email': 'me@mause.me',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Mause/duckdb_engine',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)
