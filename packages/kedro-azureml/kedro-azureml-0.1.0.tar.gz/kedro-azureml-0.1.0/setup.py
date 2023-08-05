# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kedro_azureml']

package_data = \
{'': ['*']}

install_requires = \
['adlfs>=2022.2.0',
 'azure-ai-ml>=0.1.0b4',
 'cloudpickle>=2.1.0,<3.0.0',
 'kedro>=0.18.2,<0.19',
 'pydantic>=1.9.1,<1.10.0']

extras_require = \
{'mlflow': ['azureml-mlflow>=1.42.0', 'mlflow>=1.27.0,<2.0.0']}

entry_points = \
{'kedro.project_commands': ['azureml = kedro_azureml.cli:commands']}

setup_kwargs = {
    'name': 'kedro-azureml',
    'version': '0.1.0',
    'description': 'Kedro plugin with Azure ML Pipelines support',
    'long_description': '# Kedro Azure ML Pipelines plugin\n\n[![Python Version](https://img.shields.io/pypi/pyversions/kedro-azureml)](https://github.com/getindata/kedro-azureml)\n[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n[![SemVer](https://img.shields.io/badge/semver-2.0.0-green)](https://semver.org/)\n[![PyPI version](https://badge.fury.io/py/kedro-azureml.svg)](https://pypi.org/project/kedro-azureml/)\n[![Downloads](https://pepy.tech/badge/kedro-azureml)](https://pepy.tech/project/kedro-azureml)\n\n[![Maintainability](https://api.codeclimate.com/v1/badges/8ecc057c4e66eb565669/maintainability)](https://codeclimate.com/github/getindata/kedro-azureml/maintainability)\n[![Test Coverage](https://api.codeclimate.com/v1/badges/8ecc057c4e66eb565669/test_coverage)](https://codeclimate.com/github/getindata/kedro-azureml/test_coverage)\n[![Documentation Status](https://readthedocs.org/projects/kedro-vertexai/badge/?version=latest)](https://kedro-azureml.readthedocs.io/en/latest/?badge=latest)\n\n\n## About\nFollowing plugin enables running Kedro pipelines on Azure ML Pipelines service\n\n## Documentation \n\nFor detailed documentation refer to https://kedro-azureml.readthedocs.io/\n\n## Usage guide\n\n```\nUsage: kedro azureml [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  -e, --env TEXT  Environment to use.\n  -h, --help      Show this message and exit.\n\nCommands:\n  compile  Compiles the pipeline into YAML format\n  init     Creates basic configuration for Kedro AzureML plugin\n  run      Runs the specified pipeline in Azure ML Pipelines\n```\n\nFollow **quickstart** section on [kedro-azureml.readthedocs.io](https://kedro-azureml.readthedocs.io/) to get up to speed with plugin usage. \n\n\n',
    'author': 'marcin.zablocki',
    'author_email': 'marcin.zablocki@getindata.com',
    'maintainer': 'GetInData',
    'maintainer_email': 'mlops@getindata.com',
    'url': 'https://github.com/getindata/kedro-azureml/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
