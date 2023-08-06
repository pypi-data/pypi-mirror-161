# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgconnection', 'pgconnection.tests']

package_data = \
{'': ['*']}

install_requires = \
['django>=2']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

setup_kwargs = {
    'name': 'django-pgconnection',
    'version': '1.0.3',
    'description': 'Route postgres connections and hook into cursor execution',
    'long_description': "django-pgconnection\n###################\n\n``django-pgconnection`` provides primitives for overriding Postgres\nconnection and cursor objects, making it possible to do the following:\n\n1. Hook into SQL generation. For example, it is not possible to log\n   every time a SQL statement is executed in Django or annotate SQL\n   with comments so that additional metadata is logged when executing\n   queries. The `pgconnection.pre_execute_hook` context manager allows\n   one to hook into SQL before it is executed.\n2. Route database traffic to a different database. Although Django provides\n   the ability to construct custom database routers, routing to a different\n   database has to be instrumented throughout code and can be tedious\n   and error prone. The `pgconnection.route` context manager can route\n   any database operations to a different database, even if it's an external\n   management command that has not been instrumented to use a different\n   database.\n\nThe `documentation <https://django-pgconnection.readthedocs.io/>`_ has\nexamples of how to use ``django-pgconnection``.\n\nDocumentation\n=============\n\n`View the django-pgconnection docs here\n<https://django-pgconnection.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall django-pgconnection with::\n\n    pip3 install django-pgconnection\n\nAfter this, add ``pgconnection`` to the ``INSTALLED_APPS``\nsetting of your Django project.\n\nIn order to use connection routing and hooks, one must configure\nthe ``DATABASES`` setting in ``settings.py`` like so::\n\n    DATABASES = pgconnection.configure({\n        'default': {\n            'ENGINE': 'django.db.backends.sqlite3',\n            'NAME': 'mydatabase',\n        }\n    })\n\nContributing Guide\n==================\n\nFor information on setting up django-pgconnection for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall)\n",
    'author': 'Wes Kendall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/django-pgconnection',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
