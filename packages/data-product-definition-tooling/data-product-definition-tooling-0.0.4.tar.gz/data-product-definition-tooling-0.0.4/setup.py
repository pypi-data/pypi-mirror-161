# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['converter',
 'converter.tests',
 'converter.tests.data.AirQuality',
 'converter.tests.data.Weather.Current']

package_data = \
{'': ['*'], 'converter.tests': ['__snapshots__/test_converter/*']}

install_requires = \
['deepdiff>=5.8.0,<6.0.0',
 'fastapi>=0.70.1,<0.71.0',
 'stringcase>=1.2.0,<2.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['converter = converter.cli:cli']}

setup_kwargs = {
    'name': 'data-product-definition-tooling',
    'version': '0.0.4',
    'description': 'Data Product Definition Tooling',
    'long_description': '# Data Product Definitions tooling\n\nTools for managing Data Product definitions\n\n# Installation\n\n```shell\npoetry install\n```\n\n# Usage\n\n```shell\npoetry run converter --help\n\n# run tests\npoetry run invoke test\n\n# release a new version (after bumping it in pyproject.toml)\npoetry run invoke release\n```\n\n## Pre-commit hooks\n\n```yaml\nrepos:\n  - repo: https://github.com/ioxio-nexus/data-product-definition-tooling\n    rev: main # You probably want to lock this to a specific tag\n    hooks:\n      - id: data-product-definition-converter\n        files: "src/.*py$"\n        args: ["src", "dest"]\n```\n',
    'author': 'Digital Living International Ltd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ioxio-nexus/data-product-definition-tooling',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9.0,<4',
}


setup(**setup_kwargs)
