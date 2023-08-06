# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scraper']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'scraper-api',
    'version': '0.1.0',
    'description': 'CI/CD pipelines for scraper library',
    'long_description': '# ci-cd-example\n\nci-cd-example\n\nCI/CD pipelines for scraper library\n\n\n## Get started\n\n\n#### Install requirements & pre-commit hooks\n\n```bash\n$ make setup\n```\n\n#### Testing\n```bash\n$ make test\n```\n\n#### Documentation\n\n##### Locally\n\nServe docs locally\n\n```bash\n$ make docs-dev\n```\n\n##### Build site\n\n```bash\n$ make docs-build\n```\n\n\n#### Linters requirements & pre-commit hooks\n\n##### Run flake8\n\n```bash\n$ make lint\n```\n\n##### Run black & isort\n\n```bash\n$ make black\n```\n',
    'author': 'Daniil Trotsenko',
    'author_email': 'daniil.trotsenko.dev@gmail.com',
    'maintainer': 'Daniil Trotsenko',
    'maintainer_email': 'daniil.trotsenko.dev@gmail.com',
    'url': 'https://github.com/danik-tro/scraper-ci-cd-library',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
