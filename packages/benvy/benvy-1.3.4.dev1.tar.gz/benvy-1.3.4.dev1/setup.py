# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['benvy',
 'benvy.container',
 'benvy.databricks',
 'benvy.databricks.api',
 'benvy.databricks.dbutils',
 'benvy.databricks.notebook',
 'benvy.databricks.repos',
 'benvy.databricks.repos.config',
 'benvy.databricks.repos.export',
 'benvy.databricks.repos.install',
 'benvy.databricks.repos.poetry',
 'benvy.databricks.repos.pylint',
 'benvy.databricks.repos.runner',
 'benvy.databricks.repos.setup',
 'benvy.databricks.repos.uploader',
 'benvy.git',
 'benvy.hadoop',
 'benvy.java',
 'benvy.mutex']

package_data = \
{'': ['*'], 'benvy.databricks': ['repos/pylint/icons/*']}

install_requires = \
['penvy>=1.2.2,<2.0.0']

entry_points = \
{'console_scripts': ['benvy-init = benvy.init:main']}

setup_kwargs = {
    'name': 'benvy',
    'version': '1.3.4.dev1',
    'description': 'Daipe framework development environment initializer',
    'long_description': "# Development environment initialization\n\nfor the [Daipe stack](https://docs.daipe.ai/)\n\n### What it does\n\n#### Local Computer\n\n* Extends the [Pyfony dev environment initialization](https://github.com/pyfony/penvy)\n* Downloads Hadoop's `winutils.exe` and puts it into the project's `.venv` directory (Windows only) \n* Downloads **Java 1.8** binaries and puts them into the `~/.databricks-connect-java` dir\n* Creates the empty `~/.databricks-connect` file\n\n#### Databricks Repos Environment\n\n* Download and install poetry package manager\n* Install dependencies from poetry.lock\n* Set current working directory to project root\n* Append src folder to sys path\n* Set proper environment variables\n\n**Usage**\n\n```\n%sh\npip install benvy==1.3.3\n```\n\n```\nfrom benvy.databricks.repos import bootstrap  # noqa\n\nbootstrap.install()\n```\n\n```\nfrom benvy.databricks.repos import bootstrap  # noqa\n\nbootstrap.setup_env()\n```\n",
    'author': 'Jiri Koutny',
    'author_email': 'jiri.koutny@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daipe-ai/benvy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
