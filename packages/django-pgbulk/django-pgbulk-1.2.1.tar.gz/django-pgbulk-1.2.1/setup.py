# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgbulk', 'pgbulk.tests']

package_data = \
{'': ['*']}

install_requires = \
['django>=2']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

setup_kwargs = {
    'name': 'django-pgbulk',
    'version': '1.2.1',
    'description': 'Native postgres bulk update and upsert operations.',
    'long_description': 'django-pgbulk\n#############\n\n``django-pgplus``, forked from\n`django-manager-utils <https://django-manager-utils.readthedocs.io>`__,\nprovides several optimized bulk operations for Postgres:\n\n1. ``update`` - For updating a list of models in bulk. Although Django\n   provides a ``bulk_update`` in 2.2, it performs individual updates for\n   every row and does not perform a native bulk update.\n2. ``upsert`` - For doing a bulk update or insert. This function uses\n   postgres ``UPDATE ON CONFLICT`` syntax to perform an atomic upsert\n   operation. There are several options to this function that allow the\n   user to avoid touching rows if they result in a duplicate update, along\n   with returning which rows were updated, created, or untouched. Users can\n   also use ``models.F`` objects on conflicts.\n3. ``sync`` - For syncing a list of models with a table. Does a bulk\n   upsert and also deletes any rows in the source queryset that were not\n   part of the input data.\n\nFor more examples, see the\n`django-pgbulk docs <https://django-pgbulk.readthedocs.io/>`_.\n\nDocumentation\n=============\n\n`View the django-pgbulk docs here <https://django-pgbulk.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall django-pgbulk with::\n\n    pip3 install django-pgbulk\n\nAfter this, add ``pgbulk`` to the ``INSTALLED_APPS``\nsetting of your Django project.\n\nContributing Guide\n==================\n\nFor information on setting up django-pgbulk for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall)\n',
    'author': 'Wes Kendall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/django-pgbulk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
