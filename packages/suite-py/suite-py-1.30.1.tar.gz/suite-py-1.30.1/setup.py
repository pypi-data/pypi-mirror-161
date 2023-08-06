# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['suite_py',
 'suite_py.commands',
 'suite_py.lib',
 'suite_py.lib.handler',
 'suite_py.lib.requests']

package_data = \
{'': ['*'], 'suite_py.commands': ['templates/*']}

install_requires = \
['Click>=7.0',
 'Flask==1.1.2',
 'InquirerPy>=0.2.0',
 'Jinja2>=2.11,<3.0.0',
 'PyGithub>=1.51',
 'PyYaml>=5.4',
 'Werkzeug==2.0.2',
 'autoupgrade-prima>=0.6',
 'boto3>=1.17.84',
 'cement>=3.0',
 'colorama>=0.4.3',
 'halo>=0.0.28',
 'inquirer>=2.7.0',
 'itsdangerous==2.0.1',
 'kubernetes==17.17.0',
 'logzero==1.7.0',
 'markupsafe==2.0.1',
 'pptree==3.1',
 'python-dateutil>=2.8.2',
 'requests-toolbelt>=0.9.1',
 'requests>=2.26.0',
 'rich==10.1.0',
 'semver>=2.13.0',
 'termcolor>=1.1.0']

entry_points = \
{'console_scripts': ['suite-py = suite_py.cli:main']}

setup_kwargs = {
    'name': 'suite-py',
    'version': '1.30.1',
    'description': '',
    'long_description': None,
    'author': 'larrywax, EugenioLaghi, michelangelomo',
    'author_email': 'devops@prima.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
