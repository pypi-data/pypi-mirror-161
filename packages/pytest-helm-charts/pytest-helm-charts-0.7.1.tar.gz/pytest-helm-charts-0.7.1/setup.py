# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_helm_charts',
 'pytest_helm_charts.flux',
 'pytest_helm_charts.giantswarm_app_platform',
 'pytest_helm_charts.giantswarm_app_platform.apps',
 'pytest_helm_charts.k8s']

package_data = \
{'': ['*']}

install_requires = \
['Deprecated>=1.2.13,<2.0.0', 'pykube-ng>=22.6,<23', 'pytest>=6.1.2,<7.0.0']

extras_require = \
{'docs': ['mkdocs>=1.2.3,<2.0.0', 'mkapi>=1.0.14,<2.0.0']}

entry_points = \
{'pytest11': ['helm-charts = pytest_helm_charts.plugin']}

setup_kwargs = {
    'name': 'pytest-helm-charts',
    'version': '0.7.1',
    'description': 'A plugin to provide different types and configs of Kubernetes clusters that can be used for testing.',
    'long_description': '# pytest-helm-charts\n\n[![build](https://github.com/giantswarm/pytest-helm-charts/workflows/build/badge.svg)](https://github.com/giantswarm/pytest-helm-charts/workflows/build/badge.svg)\n[![codecov](https://codecov.io/gh/giantswarm/pytest-helm-charts/branch/master/graph/badge.svg)](https://codecov.io/gh/giantswarm/pytest-helm-charts)\n[![Documentation Status](https://readthedocs.org/projects/pytest-helm-charts/badge/?version=latest)](https://pytest-helm-charts.readthedocs.io/en/latest/?badge=latest)\n[![PyPI Version](https://img.shields.io/pypi/v/pytest-helm-charts.svg)](https://pypi.org/project/pytest-helm-charts/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/pytest-helm-charts.svg)](https://pypi.org/project/pytest-helm-charts/)\n[![Apache License](https://img.shields.io/badge/license-apache-blue.svg)](https://pypi.org/project/pytest-helm-charts/)\n\nA plugin to test helm charts on Kubernetes clusters.\n\nFull documentation (including API) available on <https://pytest-helm-charts.readthedocs.io/>.\n\n---\n\n## Features\n\nThis plugin provides a set of [pytest](https://docs.pytest.org/) fixtures that allow you to easily\nwrite tests for Helm charts and run them on Kubernetes clusters.\n\nIt can be also used to test Helm charts deployed using the Open Source\n[Giant Swarm App Platform](https://docs.giantswarm.io/basics/app-platform/).\n\nMost important features:\n\n- provides [pykube-ng](http://pykube.readthedocs.io/) interface to access Kubernetes clusters\n- provides [command line options](#usage) to configure the target cluster to run on\n- provides fixtures to work with some standard Kubernetes resources as well as some custom ones:\n  - [Kubernetes objects](pytest_helm_charts.k8s)\n  - [Giant Swarm App Platform objects](pytest_helm_charts.giantswarm_app_platform)\n  - [Flux CD objects](pytest_helm_charts.flux)\n- provides set of fixtures to easily work with Helm charts\n\n## Requirements\n\nPlease check `[tool.poetry.dependencies]` list in the [`pyproject.toml`](pyproject.toml) file.\n\n## Installation\n\nYou can install "pytest-helm-charts" via `pip` from `PyPI`:\n\n```bash\npip install pytest-helm-charts\n```\n\n## Usage\n\n### Running your tests\n\nWhen you want to run your tests, you invoke `pytest` as usual, just passing additional\nflags on the command line. You can inspect them directly by running `pytest -h` and\nchecking the "helm-charts" section.\n\nCurrently, the only supported cluster type is `external`, which means the cluster is not\nmanaged by the test suite. You just point the test suite to a `kube.config` file,\nwhich can be used to connect to the Kubernetes API with `--kube-config` command line\noption. For creating development time clusters, we recommend using\n[KinD](https://kind.sigs.k8s.io/).\n\nIf you use this project to test Helm charts against Giant Swarm App Platform, the `existing`\ncluster must already have the platform components installed. Please refer to and use\nthe [`app-test-suite`](https://github.com/giantswarm/app-test-suite) tool to easily\ncreate `KinD` based clusters with all the components already installed.\n\n### Writing tests\n\nThe easiest way to get started is by checking our\n[examples](https://pytest-helm-charts.readthedocs.io/en/latest/examples/basic).\n\nThe list of available fixtures can be found by running `pytest --fixtures`, but\nyou can also just check [the most important fixtures](docs/fixtures.md).\n\nFull [API docs](https://pytest-helm-charts.readthedocs.io/en/latest/api/pytest_helm_charts/)\nare also available.\n\n## Contributing\n\nContributions are very welcome.\n\n- Project is managed with [`poetry`](https://python-poetry.org/),\n  to start developing run `poetry install`\n- Tests for all supported python versions can be run with [`tox`](https://tox.readthedocs.io/):\n  `poetry run tox -- --log-cli-level info tests/`\n- Please ensure\n  [the coverage](https://codecov.io/gh/giantswarm/pytest-helm-charts/)\n  at least stays the same before you submit a pull request.\n\n## License\n\nSee [LICENSE](LICENSE).\n\n## Changelog\n\nSee [CHANGELOG.md](CHANGELOG.md).\n\n## Issues\n\nIf you encounter any problems, please [file an issue](https://github.com/giantswarm/pytest-helm-charts/issues)\nalong with a detailed description.\n',
    'author': 'Łukasz Piątkowski',
    'author_email': 'lukasz@giantswarm.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/giantswarm/pytest-helm-charts',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
