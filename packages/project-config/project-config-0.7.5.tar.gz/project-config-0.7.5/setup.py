# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['project_config',
 'project_config.config',
 'project_config.config.style',
 'project_config.fetchers',
 'project_config.plugins',
 'project_config.reporters',
 'project_config.serializers',
 'project_config.tests',
 'project_config.tests.pytest_plugin',
 'project_config.utils']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1,<2',
 'colored',
 'deepmerge>=1.0.1,<2.0.0',
 'diskcache>=5,<6',
 'identify>=2,<3',
 'importlib-metadata-argparse-version',
 'jmespath>=1,<2',
 'pyjson5',
 'requests-futures>=1.0.0,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'ruamel.yaml>=0.17,<0.18',
 'tabulate>=0.8,<0.9',
 'tomli-w>=1,<2',
 'tomlkit>=0.11.1,<0.12.0',
 'typing-extensions>=4.3.0,<5.0.0']

extras_require = \
{':python_version < "3.10"': ['importlib-metadata'],
 ':python_version < "3.11"': ['tomli>=2,<3']}

entry_points = \
{'console_scripts': ['project-config = project_config.__main__:main'],
 'project_config.plugins': ['existence = '
                            'project_config.plugins.existence:ExistencePlugin',
                            'inclusion = '
                            'project_config.plugins.inclusion:InclusionPlugin',
                            'jmespath = '
                            'project_config.plugins.jmespath:JMESPathPlugin'],
 'pytest11': ['project-config-tester = '
              'project_config.tests.pytest_plugin.plugin']}

setup_kwargs = {
    'name': 'project-config',
    'version': '0.7.5',
    'description': 'Reproducible configuration across projects.',
    'long_description': '# project-config\n\n[![PyPI][pypi-version-badge-link]][pypi-link]\n[![Python versions][pypi-pyversions-badge-link]][pypi-link]\n[![License][license-image]][license-link]\n[![Tests][tests-image]][tests-link]\n[![Coverage][coverage-image]][coverage-link]\n[![Downloads][pypi-downloads-image]][pypi-downloads-link]\n\n\n> Note for developers: This project is under heavy development.\nThe testing and reporter APIs may change without warning before the\nfirst stable release (v1), but configuration, CLI and plugins are\nguaranteed to be backwards compatible, so you can safely write\nstyles now.\n\n## [Documentation](https://mondeja.github.io/project-config/latest/)\n\nLint the data files of your projects in a flexible way using JMESPaths.\n\n### `project-config check`\n\n![project-config check](https://raw.githubusercontent.com/mondeja/project-config/master/docs/_static/img/project-config-check.png)\n\n### `project-config fix`\n\n![project-config fix](https://raw.githubusercontent.com/mondeja/project-config/master/docs/_static/img/project-config-fix.png)\n\n[pypi-link]: https://pypi.org/project/project-config\n[pypi-version-badge-link]: https://img.shields.io/pypi/v/project-config?logo=pypi&logoColor=white\n[pypi-pyversions-badge-link]: https://img.shields.io/pypi/pyversions/project-config?logo=python&logoColor=white\n[license-image]: https://img.shields.io/pypi/l/project-config?color=light-green&logo=freebsd&logoColor=white\n[license-link]: https://github.com/mondeja/project-config/blob/master/LICENSE\n[tests-image]: https://img.shields.io/github/workflow/status/mondeja/project-config/CI?logo=github&label=tests\n[tests-link]: https://github.com/mondeja/project-config/actions?query=workflow%3ACI\n[pypi-downloads-image]: https://img.shields.io/pypi/dm/project-config?logo=pypi&logoColor=white\n[pypi-downloads-link]: https://pypistats.org/packages/project-config\n[coverage-image]: https://img.shields.io/coveralls/github/mondeja/project-config?logo=coveralls\n[coverage-link]: https://coveralls.io/github/mondeja/project-config\n',
    'author': 'Álvaro Mondéjar Rubio',
    'author_email': 'mondejar1994@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mondeja/project-config',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
