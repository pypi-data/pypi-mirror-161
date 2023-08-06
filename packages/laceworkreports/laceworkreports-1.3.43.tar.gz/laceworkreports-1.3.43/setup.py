# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['laceworkreports',
 'laceworkreports.cli.ExportHandlers',
 'laceworkreports.cli.ExportHandlers.ActivitiesHandler',
 'laceworkreports.cli.ExportHandlers.ConfigsHandler',
 'laceworkreports.cli.ExportHandlers.DataExportHandlers',
 'laceworkreports.cli.ExportHandlers.EntitiesHandler',
 'laceworkreports.cli.ExportHandlers.QueriesHandler',
 'laceworkreports.cli.ExportHandlers.VulnerabilitiesHandler',
 'laceworkreports.cli.ReportHandlers',
 'laceworkreports.cli.ReportHandlers.AgentCoverageHandler',
 'laceworkreports.cli.ReportHandlers.ComplianceCoverageHandler',
 'laceworkreports.cli.ReportHandlers.ContainerIntegrationCoverageHandler',
 'laceworkreports.cli.ReportHandlers.ContainerVulnerabilityCoverageHandler',
 'laceworkreports.cli.ReportHandlers.VpcChartHandler',
 'laceworkreports.cli.ReportHandlers.VulnerabilityCoverageHandler',
 'laceworkreports.sdk']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'SQLAlchemy-Utils>=0.38.2,<0.39.0',
 'SQLAlchemy>=1.4.32,<2.0.0',
 'anaconda>=0.0.1,<0.0.2',
 'click==8.0.4',
 'importlib-metadata>=4.10.1,<5.0.0',
 'laceworksdk>=1.1.0,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'networkx>=2.8,<3.0',
 'pandas>=1.4.1,<2.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'rich>=10.14,<13.0',
 'typer[all]>=0.4.0,<0.5.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=4.5.0,<5.0.0'],
 ':python_version >= "3.8" and python_version < "3.11"': ['scipy>=1.8.0,<2.0.0']}

entry_points = \
{'console_scripts': ['laceworkreports = laceworkreports.__main__:app']}

setup_kwargs = {
    'name': 'laceworkreports',
    'version': '1.3.43',
    'description': 'laceworkreports is a Python cli/package for creating reports from Lacework data.',
    'long_description': '# Lacework Reports CLI/SDK\n\n<div align="center">\n\n[![Build status](https://github.com/laceworkps/laceworkreports/workflows/build/badge.svg?branch=main&event=push)](https://github.com/laceworkps/laceworkreports/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/laceworkreports.svg)](https://pypi.org/project/laceworkreports/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/laceworkps/laceworkreports/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/laceworkps/laceworkreports/blob/main/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/laceworkps/laceworkreports/releases)\n[![License](https://img.shields.io/github/license/laceworkps/laceworkreports)](https://github.com/laceworkps/laceworkreports/blob/main/LICENSE)\n![Coverage Report](assets/images/coverage.svg)\n\nlaceworkreports is a Python cli/package for creating reports from Lacework data.\n\n</div>\n\n## 🚀 Features\n\n- Retrieve Lacework API data from activities, entities, queries, configs\n- Save results as csv, json, or to postgres\n- Transform results using jinja template\n- Override returned field names using field_map (supports nested json notation: parent.child.value)\n- Stores complex json objects as JSONB in postgres\n- Flatten json structures before writing\n\n## CLI Usage\n\n```bash\nlaceworkreports export vulnerabilities hosts csv --file-path="export.csv"\n```\n\n![laceworkreports](assets/images/laceworkreports.gif)\n\nSee [CLI README](README-CLI.md) for details.\n\n## SDK Usage\n\n```python\nfrom laceworkreports import common\nfrom laceworkreports.sdk.DataHandlers import (\n    DataHandlerTypes,\n    ExportHandler,\n    QueryHandler,\n)\n\neh = ExportHandler(\n    format=DataHandlerTypes.CSV,\n    results=QueryHandler(\n        client=LaceworkClient(),\n        type=common.ObjectTypes.Activities.value,\n        object=common.ActivitiesTypes.DNSSummaries.value,\n        filters=[{"field": "mid", "expression": "eq", "value": 851}],\n        returns=["fqdn"],\n    ).execute(),\n    file_path="export.csv",\n).export()\n```\n\nSee [example.py](examples/sdk/example.py) for details.\n\n## Installation\n\n```bash\npip install -U laceworkreports\n```\n\nor install with `Poetry`\n\n```bash\npoetry add laceworkreports\n```\n\nThen you can run\n\n```bash\nlaceworkreports --help\n```\n\nor with `Poetry`:\n\n```bash\npoetry run laceworkreports --help\n```\n\nor run with `docker`:\n\n```bash\ndocker run --rm -it --name laceworkreports \\\n    -v ~/.lacework.toml:/home/user/.lacework.toml -v $(pwd)/reports:/app/reports \\\n    laceworkps/laceworkreports:latest --help\n```\n\nor run with `docker` and start a shell:\n\n```bash\ndocker run --rm --entrypoint="/bin/bash" -it --name laceworkreports \\\n    -v ~/.lacework.toml:/home/user/.lacework.toml -v $(pwd)/reports:/app/reports \\\n    laceworkps/laceworkreports:latest --help\n```\n\nor run with `docker` and force uid:gid on the volume mount (may be required for write permissions):\n\n```bash\ndocker run --rm -it \\\n    --name laceworkreports \\\n    -v ~/.lacework.toml:/home/user/.lacework.toml \\\n    -v $(pwd)/reports:/app/reports \\\n    --env=HOME=/home/user \\\n    --user $UID:$GID \\\n    laceworkps/laceworkreports:latest\n```\n\n## 📈 Releases\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/laceworkps/laceworkreports/releases) page.\n\nWe follow [Semantic Versions](https://semver.org/) specification.\n\nWe use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.\n\n### List of labels and corresponding titles\n\n|               **Label**               |  **Title in Releases**  |\n| :-----------------------------------: | :---------------------: |\n|       `enhancement`, `feature`        |       🚀 Features       |\n| `bug`, `refactoring`, `bugfix`, `fix` | 🔧 Fixes & Refactoring  |\n|       `build`, `ci`, `testing`        | 📦 Build System & CI/CD |\n|              `breaking`               |   💥 Breaking Changes   |\n|            `documentation`            |    📝 Documentation     |\n|            `dependencies`             | ⬆️ Dependencies updates |\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/laceworkps/laceworkreports)](https://github.com/laceworkps/laceworkreports/blob/main/LICENSE)\n\nThis project is licensed under the terms of the `BSD-3` license. See [LICENSE](https://github.com/laceworkps/laceworkreports/blob/main/LICENSE) for more details.\n\n## 📃 Citation\n\n```bibtex\n@misc{laceworkreports,\n  author = {Lacework Inc.},\n  title = {laceworkreports is a Python cli/package for creating reports from Lacework data.},\n  year = {2022},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/laceworkps/laceworkreports}}\n}\n```\n',
    'author': 'Lacework Inc.',
    'author_email': 'jamie.mcmurray@lacework.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/laceworkps/laceworkreports',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
