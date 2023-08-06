# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saigen_dep_test_with_poetry']

package_data = \
{'': ['*']}

install_requires = \
['SoundFile>=0.10.3,<0.11.0',
 'boto3>=1.24.40,<2.0.0',
 'librosa>=0.9.2,<0.10.0',
 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'saigen-dep-test-with-poetry',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'francois_saigen',
    'author_email': 'francois@saigen.co.za',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
