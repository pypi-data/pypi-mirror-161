# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forgedb', 'forgedb.management', 'forgedb.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.0',
 'dj-database-url>=1.0.0,<2.0.0',
 'forge-core>=0.4.0,<1.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'requests>=2.0.0']

entry_points = \
{'console_scripts': ['forge-db = forgedb:cli']}

setup_kwargs = {
    'name': 'forge-db',
    'version': '0.3.0',
    'description': 'Work library for Forge',
    'long_description': '# forge-db\n\nUse Postgres for local Django development via Docker.\n\n\n## Installation\n\n### Forge installation\n\nThe `forge-db` package is a dependency of [`forge`](https://github.com/forgepackages/forge) and is available as `forge db`.\n\nIf you use the [Forge quickstart](https://www.forgepackages.com/docs/quickstart/),\neverything you need will already be set up.\n\nThe [standard Django installation](#standard-django-installation) can give you an idea of the steps involved.\n\n\n### Standard Django installation\n\nThis package can be used without `forge` by installing it as a regular Django app.\n\nFirst, install `forge-db` from [PyPI](https://pypi.org/project/forge-db/):\n\n```sh\npip install forge-db\n```\n\nThen add it to your `INSTALLED_APPS` in `settings.py`:\n\n```python\nINSTALLED_APPS = [\n    ...\n    "forgedb",\n]\n```\n\nNow you will have access to the `db` command:\n\n```sh\npython manage.py db\n```\n\nYou will need to have a `DATABASE_URL` environment variable,\nwhich is where the database name, username, password, and port are parsed from:\n\n```sh\n# .env\nDATABASE_URL=postgres://postgres:postgres@localhost:54321/postgres\n```\n\nYou can use a `POSTGRES_VERSION` environment variable to override the default Postgres version (13):\n\n```sh\n# .env\nPOSTGRES_VERSION=12\n```\n\nIn most cases you will want to use [`dj_database_url`](https://github.com/kennethreitz/dj-database-url) in your `settings.py` to easily set the same settings (works in most deployment environments too):\n\n```python\n# settings.py\nimport dj_databse_url\n\nDATABASES = {\n    "default": dj_database_url.parse(\n        environ["DATABASE_URL"], conn_max_age=environ.get("DATABASE_CONN_MAX_AGE", 600)\n    )\n}\n```\n\nYou will also notice a new `.forge` directory in your project root.\nThis contains your local database files and should be added to `.gitignore`.\n\n## Usage\n\nIf you use [`forge-work`](https://github.com/forgepackages/forge-work),\nthen most of the time you won\'t need to interact with `forge-db` directly.\nBut it has a few commands that come in handy.\n\n- `forge db start` - starts a new database container and runs it in the background (use `--logs` to foreground it or connect to the logs)\n- `forge db stop` - stop the database container\n- `forge db reset` - drops and creates a new database\n- `forge db pull` - pulls the latest database backup from Heroku and imports it into the local database\n\nIn the end, the database container is like any other Docker container.\nYou can use the standard Docker commands and tools to interact with it when needed.\n',
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.forgepackages.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
