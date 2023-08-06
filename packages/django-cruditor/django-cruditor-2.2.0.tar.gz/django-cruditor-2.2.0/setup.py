# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cruditor']

package_data = \
{'': ['*'],
 'cruditor': ['client/js/*',
              'client/js/components/*',
              'client/scss/*',
              'locale/de/LC_MESSAGES/*',
              'locale/fr/LC_MESSAGES/*',
              'static/cruditor/css/*',
              'static/cruditor/js/*',
              'templates/cruditor/*',
              'templates/cruditor/forms/*',
              'templates/cruditor/includes/*']}

install_requires = \
['Django>=2.2']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata'],
 'docs': ['Sphinx>=3.5',
          'django-tapeforms>=1.1.0',
          'django-tables2>=2.4.1',
          'django-filter>=21.1']}

setup_kwargs = {
    'name': 'django-cruditor',
    'version': '2.2.0',
    'description': 'A set of class based views and mixins to generate CRUD interfaces.',
    'long_description': "django-cruditor\n===============\n\n.. image:: https://img.shields.io/pypi/v/django-cruditor.svg\n   :target: https://pypi.org/project/django-cruditor/\n   :alt: Latest Version\n\n.. image:: https://github.com/stephrdev/django-cruditor/workflows/Test/badge.svg?branch=master\n   :target: https://github.com/stephrdev/django-cruditor/actions?workflow=Test\n   :alt: CI Status\n\n.. image:: https://codecov.io/gh/stephrdev/django-cruditor/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/stephrdev/django-cruditor\n   :alt: Coverage Status\n\n.. image:: https://readthedocs.org/projects/django-cruditor/badge/?version=latest\n   :target: https://django-cruditor.readthedocs.io/en/stable/?badge=latest\n   :alt: Documentation Status\n\n\nUsage\n-----\n\nPlease refer to the `Documentation <https://django-cruditor.readthedocs.io/>`_ to\nlearn how to use ``django-cruditor``. Cruditor is a set of generic class based views\nwith UIKit styled templates. Together with django-tables2, django-filter and\ndjango-tapeforms this package provides you some easy to use Django views to build\nyour customized CRUD interface.\n\n\nRequirements\n------------\n\ndjango-cruditor supports Python 3 only and requires at least Django 2.2.\nOptional dependencies are django-tapeforms, django-tables2 and django-filter.\n\n\nPrepare for development\n-----------------------\n\nA Python 3 interpreter is required in addition to poetry.\n\n.. code-block:: shell\n\n    $ poetry install\n    # If you want to build docs, execute this in addition\n    $ poetry install -E docs\n\n\nNow you're ready to start the example project to experiment with cruditor.\n\n.. code-block:: shell\n\n    $ poetry run python examples/manage.py runserver\n",
    'author': 'Stephan Jaekel',
    'author_email': 'steph@rdev.info',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stephrdev/django-cruditor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4',
}


setup(**setup_kwargs)
