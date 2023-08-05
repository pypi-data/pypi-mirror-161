# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['appconfig_helper']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'boto3>=1.20.8,<2.0.0', 'botocore>=1.23.8,<2.0.0']

setup_kwargs = {
    'name': 'sample-helper-aws-appconfig',
    'version': '2.0.3',
    'description': 'Sample helper library for AWS AppConfig',
    'long_description': '# Sample AWS AppConfig Helper\n\nA sample helper Python library for AWS AppConfig which makes rolling configuration updates out easier.\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sample-helper-aws-appconfig) ![PyPI version](https://badge.fury.io/py/sample-helper-aws-appconfig.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## Features\n\n* Configurable update interval: you can ask the library to update your configuration as often as needed, but it will only call the AWS AppConfig API at the configured interval (in seconds).\n* Handles correct API usage: the library uses the new AppConfig Data API and handles tracking the next configuration token and poll interval for you.\n* Flexible: Can automatically fetch the current configuration on initialisation, every time the configuration is read by your code, or on demand. You can override the caching interval if needed.\n* Handles YAML, JSON and plain text configurations, stored in any supported AppConfig store. Any other content type is returned unprocessed as the Python `bytes` type.\n* Supports AWS Lambda, Amazon EC2 instances and on-premises use.\n\n## Installation\n\n```bash\npip install sample-helper-aws-appconfig\n```\n\n## Example\n\n```python\nfrom appconfig_helper import AppConfigHelper\nfrom fastapi import FastAPI\n\nappconfig = AppConfigHelper(\n    "MyAppConfigApp",\n    "MyAppConfigEnvironment",\n    "MyAppConfigProfile",\n    45  # minimum interval between update checks\n)\n\napp = FastAPI()\n\n@app.get("/some-url")\ndef index():\n    if appconfig.update_config():\n        print("New configuration received")\n    # your configuration is available in the "config" attribute\n    return {\n        "config_info": appconfig.config\n    }\n```\n\n## Usage\n\nPlease see the [AWS AppConfig documentation](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html) for details on configuring the service.\n\n### Initialising\n\nStart by creating an `AppConfigHelper` object. You must specify the application name, environment name, and profile (configuration) name. You must also specify the refresh interval, in seconds. AppConfigHelper will not attempt to fetch a new configuration version from the AWS AppConfig service more frequently than this interval. You should set it low enough that your code will receive new configuration promptly, but not so low that it takes too long. The library enforces a minimum interval of 15 seconds.\n\nThe configuration is not automatically fetched unless you set `fetch_on_init`. To have the library fetch the configuration when it is accessed, if it has been more than `max_config_age` seconds since the last fetch, set `fetch_on_read`.\n\nIf you need to customise the AWS credentials or region, set `session` to a configured `boto3.Session` object. Otherwise, the [standard boto3 logic](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) for credential/configuration discovery is used.\n\n### Reading the configuration\n\nThe configuration from AWS AppConfig is available as the `config` property. Before accessing it, you should call `update_config()`, unless you specified fetch_on_init or fetch_on_read during initialisation. If you want to force a config fetch, even if the number of seconds specified have not yet passed, call `update_config(True)`.\n\n`update_config()` returns `True` if a new version of the configuration was received. If no attempt was made to fetch it, or the configuration received was the same as current one, it returns `False`. It will raise `ValueError` if the received configuration data could not be processed (e.g. invalid JSON). If needed, the inner exception for JSON or YAML parsing is available as `__context__` on the raised exception.\n\nTo read the values in your configuration, access the `config` property. For JSON and YAML configurations, this will contain the structure of your data. For plain text configurations, this will be a simple string.\n\nThe original data received from AppConfig is available in the `raw_config` property. Accessing this property will not trigger an automatic update even if `fetch_on_read` is True. The content type field received from AppConfig is available in the `content_type` property.\n\nFor example, with the following JSON in your AppConfig configuration profile:\n\n```json\n{\n    "hello": "world",\n    "data": {\n        "is_sample": true\n    }\n}\n```\n\nyou would see the following when using the library:\n\n```python\n# appconfig is the instance of the library\n>>> appconfig.config["hello"]\n"world"\n>>> appconfig.config["data"]\n{\'is_sample\': True}\n```\n\n### Use in AWS Lambda\n\nAWS AppConfig is best used in Lambda by taking advantage of [Lambda Extensions](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-integration-lambda-extensions.html)\n\n## Security\n\nSee [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.\n\n## Licence\n\nThis library is licensed under Apache-2.0. See the LICENSE file.\n',
    'author': 'Amazon Web Services',
    'author_email': None,
    'maintainer': 'James Seward',
    'maintainer_email': 'sewardjm@amazon.co.uk',
    'url': 'https://github.com/aws-samples/sample-python-helper-aws-appconfig',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
