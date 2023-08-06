# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgclone',
 'pgclone.management',
 'pgclone.management.commands',
 'pgclone.tests']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.0.0,<2.0.0', 'django-pgconnection>=1.0.0,<2.0.0', 'django>=2']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

setup_kwargs = {
    'name': 'django-pgclone',
    'version': '1.0.3',
    'description': 'Dump and restore Postgres databases with Django.',
    'long_description': "django-pgclone\n##############\n\n``django-pgclone`` provides commands and utilities for doing Postgres dumps and\nrestores. In contrast with other Django database copy/restore apps\nlike `django-db-backup <https://github.com/django-dbbackup/django-dbbackup>`__,\n``django-pgclone`` has the following advantages:\n\n1. Defaults to streaming restores (when S3 is enabled) for larger databases\n   and limited instance memory.\n2. Provides hooks into the dump and restoration process, allowing users to\n   perform migrations and other user-specified management commands\n   *before* the restored database is swapped into the main one without\n   interfering with the application.\n3. Allows ``ls`` of database dumps and easily restoring the latest\n   dump of a particular database.\n\nRead the `docs <https://django-pgclone.readthedocs.io>`__ to get started\nusing the core management commands and to learn about how to configure\n``django-pgclone`` for your use case.\n\nDocumentation\n=============\n\n`View the django-pgclone docs here\n<https://django-pgclone.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall django-pgclone with::\n\n    pip3 install django-pgclone\n\nAfter this, add ``pgclone`` to the ``INSTALLED_APPS``\nsetting of your Django project.\n\n``django-pgclone`` depends on ``django-pgconnection``. Although\nthis dependency is automatically installed, one must add ``pgconnection``\nto ``settings.INSTALLED_APPS`` and also configure the\n``settings.DATABASES`` setting like so::\n\n    import pgconnection\n\n    DATABASES = pgconnection.configure({\n        'default': # normal database config goes here...\n    })\n\nContributing Guide\n==================\n\nFor information on setting up django-pgclone for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall)\n- @ethanpobrien (Ethan O'Brien)\n",
    'author': 'Wes Kendall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/django-pgclone',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
