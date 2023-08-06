# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autil']

package_data = \
{'': ['*']}

install_requires = \
['adjustText>=0.7.3,<0.8.0',
 'altair>=4.1,<5.0',
 'country_converter>=0.7.3,<0.8.0',
 'cycler>=0.10,<0.11',
 'deepl>=1.6.0,<2.0.0',
 'linearmodels>=4.24,<5.0',
 'matplotlib>=3.4,<4.0',
 'numpy>=1.21,<2.0',
 'pandas>=1.3,<2.0',
 'pyarrow>=5.0.0,<6.0.0',
 'pycountry_convert>=0.7.2,<0.8.0',
 'requests>=2.26,<3.0',
 'requests_html>=0.10,<0.11',
 'scikit_learn>=1.0,<2.0',
 'seaborn>=0.11,<0.12',
 'selenium-wire>=4.6,<5.0',
 'selenium>=3.141.0,<4.0.0',
 'tenacity>=8.0.1,<9.0.0',
 'tqdm>=4.62,<5.0',
 'translators>=4.9.5,<5.0.0']

setup_kwargs = {
    'name': 'autil',
    'version': '0.2.2',
    'description': "Some Python snippets for a researcher's daily use",
    'long_description': None,
    'author': 'alalalalaki',
    'author_email': 'harlan.zhu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
