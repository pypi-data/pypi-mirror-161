# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['migration_docs',
 'migration_docs.management',
 'migration_docs.management.commands',
 'migration_docs.tests',
 'migration_docs.tests.migrations']

package_data = \
{'': ['*']}

install_requires = \
['django>=2', 'formaldict>=1.0.0', 'jinja2>=2.11.3', 'pyyaml>=5.4']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

setup_kwargs = {
    'name': 'django-migration-docs',
    'version': '1.0.3',
    'description': 'Sync and validate additional information about your Django migrations.',
    'long_description': "django-migration-docs\n#####################\n\nMigrations can be one of the most challenging aspects of deploying a\nDjango application at scale. Depending on the size of tables and flavor\nof database, some migrations can easily lock some of the most important\ntables and bring down an application if more scrutiny isn't applied towards\ndeployed migrations. Along with this, sometimes we must document more\ncritical metadata about a migration before it is even deployed, such as\nwhen the migration should run in the deployment process.\n\n``django-migration-docs`` provides the ability to collect more structured\ninformation about every migration in your Django project. Along with this,\nit also automatically collects important metadata about migrations like\nthe raw SQL so that more information is available for reviewers and maintainers\nof a large project.\n\nWhen ``django-migration-docs`` is installed, users will be prompted for\nmore information about migrations using\na completely customizable schema that can be linted in continuous integration.\nThe default prompt looks like the following:\n\n\n.. image:: https://raw.githubusercontent.com/jyveapp/django-migration-docs/master/docs/_static/sync.gif\n    :width: 600\n\nCheck out the `docs <https://django-migration-docs.readthedocs.io/>`__ for more information\nabout how to use ``django-migration-docs`` in your application.\n\nDocumentation\n=============\n\n`View the django-migration-docs docs here\n<https://django-migration-docs.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall django-migration-docs with::\n\n    pip3 install django-migration-docs\n\nAfter this, add ``migration_docs`` to the ``INSTALLED_APPS``\nsetting of your Django project.\n\nContributing Guide\n==================\n\nFor information on setting up django-migration-docs for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\n\nPrimary Authors\n===============\n\n- @juemura (Juliana de Heer)\n- @wesleykendall (Wes Kendall)\n- @tomage (Tómas Árni Jónasson)\n",
    'author': 'Juliana de Heer',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/django-migration-docs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
