# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_assurka']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24.0,<3.0.0']

entry_points = \
{'pytest11': ['assurka = pytest_assurka.plugin']}

setup_kwargs = {
    'name': 'pytest-assurka',
    'version': '0.2.5',
    'description': 'A pytest plugin for Assurka Studio',
    'long_description': "# pytest-assurka: A pytest plugin for Assurka Studio\n\n\n# Pre-Installation\n\nThe api requests use the `requests` package and this may need to be installed first.\n\n```\npip install requests\n```\n\n# Installation\n\npip install the package to your project's virtual environment. Directly from plugin folder:\n\n\n```bash\npip install -e .\n```\n\nor pip install it from Pypi:\n```bash\npip install pytest-assurka\n```\n\nActivate the plugin with the pytest cli with the command:\n\n```bash\npytest --assurka-projectId={projectId} --assurka-secret={secret} --assurka-testPlanId={testPlanId}\n```\n\nYou can get the above keys from Assurka Studio https://studio.assurka.io",
    'author': 'Assurka Limited',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
