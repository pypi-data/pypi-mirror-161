# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['qwixtractor']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.3', 'progressbar2>=4.0.0', 'requests>=2.28.1']

setup_kwargs = {
    'name': 'qwixtractor',
    'version': '0.1.0',
    'description': 'Extract data from the Quarterly Workforce Indicators',
    'long_description': '# qwixtractor\n\nExtract data from the Quarterly Workforce Indicators\n\n## Installation\n\n```bash\n$ pip install qwixtractor\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`qwixtractor` was created by Rodrigo Franco. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`qwixtractor` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Rodrigo Franco',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
