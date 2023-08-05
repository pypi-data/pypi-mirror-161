# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splitgraph',
 'splitgraph.cloud',
 'splitgraph.cloud.project',
 'splitgraph.commandline',
 'splitgraph.config',
 'splitgraph.core',
 'splitgraph.core.indexing',
 'splitgraph.core.sql',
 'splitgraph.engine',
 'splitgraph.engine.postgres',
 'splitgraph.hooks',
 'splitgraph.hooks.data_source',
 'splitgraph.ingestion',
 'splitgraph.ingestion.airbyte',
 'splitgraph.ingestion.athena',
 'splitgraph.ingestion.bigquery',
 'splitgraph.ingestion.csv',
 'splitgraph.ingestion.dbt',
 'splitgraph.ingestion.singer',
 'splitgraph.ingestion.singer.commandline',
 'splitgraph.ingestion.snowflake',
 'splitgraph.ingestion.socrata',
 'splitgraph.resources',
 'splitgraph.resources.icons',
 'splitgraph.resources.splitgraph_meta',
 'splitgraph.resources.static',
 'splitgraph.splitfile',
 'splitgraph.splitfile.generation',
 'splitgraph.utils']

package_data = \
{'': ['*']}

install_requires = \
['asciitree>=0.3.3',
 'cffi<1.15',
 'chardet>=4.0.0,<5.0.0',
 'click>=7,<8',
 'click_log>=0.3.2',
 'cryptography>=3.4.0',
 'docker>=5.0.2',
 'jsonschema>=3.1.0',
 'minio>=4',
 'packaging>=20.1',
 'parsimonious>=0.8,<0.9',
 'psycopg2-binary>=2,<3',
 'pydantic>=1.8.1',
 'requests>=2.22',
 'ruamel.yaml>=0.17.17,<0.18.0',
 'sodapy>=2.1',
 'splitgraph-pipelinewise-target-postgres>=2.1.0',
 'tabulate>=0.8.7',
 'tqdm>=4.46.0']

extras_require = \
{':sys_platform != "win32"': ['pglast==3.4'],
 'pandas': ['pandas[ingestion]==1.1.5', 'sqlalchemy[ingestion]>=1.3,<1.4.23']}

entry_points = \
{'console_scripts': ['sgr = splitgraph.commandline:cli']}

setup_kwargs = {
    'name': 'splitgraph',
    'version': '0.3.12',
    'description': 'Command line library and Python client for Splitgraph, a version control system for data',
    'long_description': '# `sgr`\n\n![Build status](https://github.com/splitgraph/sgr/workflows/build_all/badge.svg)\n[![Coverage Status](https://coveralls.io/repos/github/splitgraph/splitgraph/badge.svg?branch=master)](https://coveralls.io/github/splitgraph/splitgraph?branch=master)\n[![PyPI version](https://badge.fury.io/py/splitgraph.svg)](https://badge.fury.io/py/splitgraph)\n[![Discord chat room](https://img.shields.io/discord/718534846472912936.svg)](https://discord.gg/4Qe2fYA)\n[![Follow](https://img.shields.io/badge/twitter-@Splitgraph-blue.svg)](https://twitter.com/Splitgraph)\n\n## Overview\n\n**`sgr`** is the CLI for [**Splitgraph**](https://www.splitgraph.com), a\nserverless API for data-driven Web applications.\n\nWith addition of the optional [`sgr` Engine](engine/README.md) component, `sgr`\ncan become a stand-alone tool for building, versioning and querying reproducible\ndatasets. We use it as the storage engine for Splitgraph. It\'s inspired by\nDocker and Git, so it feels familiar. And it\'s powered by\n[PostgreSQL](https://postgresql.org), so it works seamlessly with existing tools\nin the Postgres ecosystem. Use `sgr` to package your data into self-contained\n**Splitgraph data images** that you can\n[share with other `sgr` instances](https://www.splitgraph.com/docs/getting-started/decentralized-demo).\n\nTo install the `sgr` CLI or a local `sgr` Engine, see the\n[Installation](#installation) section of this readme.\n\n### Build and Query Versioned, Reproducible Datasets\n\n[**Splitfiles**](https://www.splitgraph.com/docs/concepts/splitfiles) give you a\ndeclarative language, inspired by Dockerfiles, for expressing data\ntransformations in ordinary SQL familiar to any researcher or business analyst.\nYou can reference other images, or even other databases, with a simple JOIN.\n\n![](pics/splitfile.png)\n\nWhen you build data images with Splitfiles, you get provenance tracking of the\nresulting data: it\'s possible to find out what sources went into every dataset\nand know when to rebuild it if the sources ever change. You can easily integrate\n`sgr` your existing CI pipelines, to keep your data up-to-date and stay on top\nof changes to upstream sources.\n\nSplitgraph images are also version-controlled, and you can manipulate them with\nGit-like operations through a CLI. You can check out any image into a PostgreSQL\nschema and interact with it using any PostgreSQL client. `sgr` will capture your\nchanges to the data, and then you can commit them as delta-compressed changesets\nthat you can package into new images.\n\n`sgr` supports PostgreSQL\n[foreign data wrappers](https://wiki.postgresql.org/wiki/Foreign_data_wrappers).\nWe call this feature\n[mounting](https://www.splitgraph.com/docs/concepts/mounting). With mounting,\nyou can query other databases (like PostgreSQL/MongoDB/MySQL) or open data\nproviders (like\n[Socrata](https://www.splitgraph.com/docs/ingesting-data/socrata)) from your\n`sgr` instance with plain SQL. You can even snapshot the results or use them in\nSplitfiles.\n\n![](pics/splitfiles.gif)\n\n## Components\n\nThe code in this repository contains:\n\n- **[`sgr` CLI](https://www.splitgraph.com/docs/architecture/sgr-client)**:\n  `sgr` is the main command line tool used to work with Splitgraph "images"\n  (data snapshots). Use it to ingest data, work with Splitfiles, and push data\n  to Splitgraph.\n- **[`sgr` Engine](https://github.com/splitgraph/sgr/blob/master/engine/README.md)**: a\n  [Docker image](https://hub.docker.com/r/splitgraph/engine) of the latest\n  Postgres with `sgr` and other required extensions pre-installed.\n- **[Splitgraph Python library](https://www.splitgraph.com/docs/python-api/splitgraph.core)**:\n  All `sgr` functionality is available in the Python API, offering first-class\n  support for data science workflows including Jupyter notebooks and Pandas\n  dataframes.\n\n## Docs\n\n- [`sgr` documentation](https://www.splitgraph.com/docs/sgr-cli/introduction)\n- [Advanced `sgr` documentation](https://www.splitgraph.com/docs/sgr-advanced/getting-started/introduction)\n- [`sgr` command reference](https://www.splitgraph.com/docs/sgr/image-management-creation/checkout_)\n- [`splitgraph` package reference](https://www.splitgraph.com/docs/python-api/modules)\n\nWe also recommend reading our Blog, including some of our favorite posts:\n\n- [Supercharging `dbt` with `sgr`: versioning, sharing, cross-DB joins](https://www.splitgraph.com/blog/dbt)\n- [Querying 40,000+ datasets with SQL](https://www.splitgraph.com/blog/40k-sql-datasets)\n- [Foreign data wrappers: PostgreSQL\'s secret weapon?](https://www.splitgraph.com/blog/foreign-data-wrappers)\n\n## Installation\n\nPre-requisites:\n\n- Docker is required to run the `sgr` Engine. `sgr` must have access to Docker.\n  You either need to [install Docker locally](https://docs.docker.com/install/)\n  or have access to a remote Docker socket.\n\nYou can get the `sgr` single binary from\n[the releases page](https://github.com/splitgraph/sgr/releases).\nOptionally, you can run\n[`sgr engine add`](https://www.splitgraph.com/docs/sgr/engine-management/engine-add)\nto create an engine.\n\nFor Linux and OSX, once Docker is running, install `sgr` with a single script:\n\n```bash\n$ bash -c "$(curl -sL https://github.com/splitgraph/sgr/releases/latest/download/install.sh)"\n```\n\nThis will download the `sgr` binary and set up the `sgr` Engine Docker\ncontainer.\n\nSee the\n[installation guide](https://www.splitgraph.com/docs/sgr-cli/installation) for\nmore installation methods.\n\n## Quick start guide\n\nYou can follow the\n[quick start guide](https://www.splitgraph.com/docs/sgr-advanced/getting-started/five-minute-demo)\nthat will guide you through the basics of using `sgr` with Splitgraph or\nstandalone.\n\nAlternatively, `sgr` comes with plenty of [examples](https://github.com/splitgraph/sgr/tree/master/examples) to get you\nstarted.\n\nIf you\'re stuck or have any questions, check out the\n[documentation](https://www.splitgraph.com/docs/sgr-advanced/getting-started/introduction)\nor join our [Discord channel](https://discord.gg/4Qe2fYA)!\n\n## Contributing\n\n### Setting up a development environment\n\n- `sgr` requires Python 3.7 or later.\n- Install [Poetry](https://github.com/python-poetry/poetry):\n  `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python`\n  to manage dependencies\n- Install pre-commit hooks (we use [Black](https://github.com/psf/black) to\n  format code)\n- `git clone --recurse-submodules https://github.com/splitgraph/sgr.git`\n- `poetry install`\n- To build the\n  [engine](https://www.splitgraph.com/docs/architecture/splitgraph-engine)\n  Docker image: `cd engine && make`\n\n### Running tests\n\nThe test suite requires [docker-compose](https://github.com/docker/compose). You\nwill also need to add these lines to your `/etc/hosts` or equivalent:\n\n```\n127.0.0.1       local_engine\n127.0.0.1       remote_engine\n127.0.0.1       objectstorage\n```\n\nTo run the core test suite, do\n\n```\ndocker-compose -f test/architecture/docker-compose.core.yml up -d\npoetry run pytest -m "not mounting and not example"\n```\n\nTo run the test suite related to "mounting" and importing data from other\ndatabases (PostgreSQL, MySQL, Mongo), do\n\n```\ndocker-compose -f test/architecture/docker-compose.core.yml -f test/architecture/docker-compose.mounting.yml up -d\npoetry run pytest -m mounting\n```\n\nFinally, to test the\n[example projects](https://github.com/splitgraph/sgr/tree/master/examples),\ndo\n\n```\n# Example projects spin up their own engines\ndocker-compose -f test/architecture/docker-compose.core.yml -f test/architecture/docker-compose.core.yml down -v\npoetry run pytest -m example\n```\n\nAll of these tests run in\n[CI](https://github.com/splitgraph/sgr/actions).\n',
    'author': 'Splitgraph Limited',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.splitgraph.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
