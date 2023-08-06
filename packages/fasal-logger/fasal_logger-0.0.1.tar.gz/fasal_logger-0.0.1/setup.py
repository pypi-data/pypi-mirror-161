# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fasal_logger']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==6.0', 'ecs-logging==2.0.0', 'slack-sdk==3.18.1']

setup_kwargs = {
    'name': 'fasal-logger',
    'version': '0.0.1',
    'description': 'json based python logger with support for slack notification',
    'long_description': '**Note:** Set up ssh key in your bitbucket account, if not already set.\n([refer this link](https://support.atlassian.com/bitbucket-cloud/docs/set-up-an-ssh-key/))\n\n-----------\n### Installation\nInstall the package using the following command\n```bash\npip install git+ssh://git@bitbucket.org/wolkustechnologysolutions/fasal_logger.git\n```\n\n--------------\n### Configuration\n- Create a file `logger.yml`. Copy the contents from the repository and make the necessary changes (If needed)\n- The logger defined here defaults to console. In order to log the contents into a file, make the required changes to the `logger.yml`.\n``` yaml\nroot:\n  handlers: [console, file]\n\nloggers:\n  fasalLogger:\n    handlers: [console, file]\n\n```\n\nAnd change the filename and location.\n```yaml\nhandler:\n    file:\n        filename: \'logging.example.log\'\n```\n\n### Usage\nIn order to use the logger in your code, add the following piece of code at the top of your .py file\n\n**Note:** `Get the webhook from the infra team to able to send messages to slack to any other channel. (By default using #fasal-ai-infra)`\n\n```python\nimport logging\nimport logging.config\nimport os\nfrom fasal_logger import LoggerInitializer, SlackNotification\n\nlogging.captureWarnings(True)\nlogger = logging.getLogger(__name__)\nlogger_init = LoggerInitializer()\nlogger_init(logger=logger, config=\'./fasal_logger/logger.yml\')\nslk = SlackNotification() # set parameter for webhook, DEV (if needed)\n\n# Use logger now\nlogger.info("Logger set")\n\n# Send a message to slack channel\nslk.notify(message="testing")\n\n```\n----------\n\n**Variables taken from environment are:**\n\n  - `SLACK_WEBHOOK`: Channel webhook trigger\n  - `DEV`: If True, no message is send to slack\n  - `ENV`: logger environment (staging/production/development)',
    'author': 'Binay Pradhan',
    'author_email': 'binay.pradhan@wolkus.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
