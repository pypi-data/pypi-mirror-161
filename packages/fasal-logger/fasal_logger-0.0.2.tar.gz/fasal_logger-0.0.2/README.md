
### Installation
Install the package using the following command
```bash
pip install fasal-logger
```

--------------
### Configuration
- Create a file `logger.yml`. Copy the contents from the repository and make the necessary changes (If needed)
- The logger defined here defaults to console. In order to log the contents into a file, make the required changes to the `logger.yml`.
``` yaml
root:
  handlers: [console, file]

loggers:
  fasalLogger:
    handlers: [console, file]

```

And change the filename and location.
```yaml
handler:
    file:
        filename: 'logging.example.log'
```

### Usage
In order to use the logger in your code, add the following piece of code at the top of your .py file

**Note:** `Get the webhook from the infra team to able to send messages to slack to any other channel. (By default using #fasal-ai-infra)`

```python
import logging
import logging.config
import os
from fasal_logger import LoggerInitializer, SlackNotification

logging.captureWarnings(True)
logger = logging.getLogger(__name__)
logger_init = LoggerInitializer()
logger_init(logger=logger, config='./fasal_logger/logger.yml')
slk = SlackNotification() # set parameter for webhook, DEV (if needed)

# Use logger now
logger.info("Logger set")

# Send a message to slack channel
slk.notify(message="testing")

```
----------

**Variables taken from environment are:**

  - `SLACK_WEBHOOK`: Channel webhook trigger
  - `DEV`: If True, no message is send to slack
  - `ENV`: logger environment (staging/production/development)

------------
Build and Published using (`poetry`)[https://python-poetry.org/docs/cli/#publish]