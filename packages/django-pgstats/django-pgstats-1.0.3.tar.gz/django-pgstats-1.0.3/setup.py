# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgstats',
 'pgstats.management',
 'pgstats.management.commands',
 'pgstats.migrations',
 'pgstats.tests']

package_data = \
{'': ['*']}

install_requires = \
['django>=2']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

setup_kwargs = {
    'name': 'django-pgstats',
    'version': '1.0.3',
    'description': 'Commands and models for tracking internal postgres stats.',
    'long_description': 'django-pgstats\n########################################################################\n\n``django-pgstats`` provides commands and models for tracking internal postgres\nstats. Specifically, the `IndexStats` model stores stats about postgres\nindices and the `TableStats` model stores stats about postgres tables.\n\nPostgres stat tables contain global statistical information. ``django-pgstats``\nis meant to be executed periodically so that one can later analyze table\nand index usage. This is done by periodically calling\n``python manage.py snapshot_pgstats`` using a task runner such\nas [Celery](http://www.celeryproject.org/).\n\nStats are stored as JSON fields in the respective `IndexStats` and `TableStats`\nmodels. Each key in the JSON field is in the format of\n``{schema}.{table}`` for table stats or ``{schema}.{table}.{index}`` for index\nstats.\n\nDocumentation\n=============\n\n`View the django-pgstats docs here\n<https://django-pgstats.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall django-pgstats with::\n\n    pip3 install django-pgstats\n\nAfter this, add ``pgstats`` to the ``INSTALLED_APPS``\nsetting of your Django project.\n\nContributing Guide\n==================\n\nFor information on setting up django-pgstats for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall)\n- @tomage (Tómas Árni Jónasson)\n',
    'author': 'Wes Kendall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/django-pgstats',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
