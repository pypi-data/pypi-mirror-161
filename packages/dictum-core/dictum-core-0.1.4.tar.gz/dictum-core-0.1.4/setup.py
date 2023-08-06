# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dictum_core',
 'dictum_core.backends',
 'dictum_core.backends.mixins',
 'dictum_core.cli',
 'dictum_core.engine',
 'dictum_core.examples',
 'dictum_core.examples.chinook',
 'dictum_core.model',
 'dictum_core.model.expr',
 'dictum_core.project',
 'dictum_core.project.altair',
 'dictum_core.project.templates',
 'dictum_core.ql',
 'dictum_core.schema',
 'dictum_core.schema.analyses',
 'dictum_core.schema.model',
 'dictum_core.tests',
 'dictum_core.tests.test_end_to_end',
 'dictum_core.tests.test_engine',
 'dictum_core.tests.test_model',
 'dictum_core.tests.test_model.configs',
 'dictum_core.tests.test_project',
 'dictum_core.tests.test_project.test_altair',
 'dictum_core.tests.test_schema',
 'dictum_core.utils']

package_data = \
{'': ['*'],
 'dictum_core.cli': ['project_template/*',
                     'project_template/metrics/*',
                     'project_template/tables/*'],
 'dictum_core.examples.chinook': ['metrics/media/*',
                                  'metrics/orders/*',
                                  'metrics/people/*',
                                  'tables/*'],
 'dictum_core.tests.test_end_to_end': ['altair_output/*']}

install_requires = \
['Babel>=2.9.1,<3.0.0',
 'Jinja2>=3.0.1,<4.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'SQLAlchemy>=1.4.25,<2.0.0',
 'altair==4.2.0rc1',
 'jupyter>=1.0.0,<2.0.0',
 'lark>=0.11.3,<0.12.0',
 'pandas>=1.3.3,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'rich>=12.5.1,<13.0.0',
 'sqlparse>=0.4.2,<0.5.0',
 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['dictum = dictum_core.cli:app']}

setup_kwargs = {
    'name': 'dictum-core',
    'version': '0.1.4',
    'description': 'Core library for Dictum',
    'long_description': None,
    'author': 'Mikhail Akimov',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
