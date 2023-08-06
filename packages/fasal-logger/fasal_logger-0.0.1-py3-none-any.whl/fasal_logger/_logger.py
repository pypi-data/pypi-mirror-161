import ecs_logging
import os
import warnings
from typing import Any, Union
from datetime import datetime


class FasalStdlibFormatter(ecs_logging.StdlibFormatter):
    def __init__(self, datefmt=None, extra=None, exclude_fields=()):
        
        # Keep required keys and default values
        self._required = {
            'severity': '',
            'source': '',
            'env': os.getenv('ENV', ''),
            'type': 'app-log',
            'message': '',
            'label': ''
        }

        # Rename any key with custom field
        # nested dict can be renamed with dot operator
        self._rename_field = {
            'severity': 'log.level',
        }

        # Copy a filed value without deleting
        self._copy_field = {
            "source": 'log.origin.file.name'
        }

        if extra is not None:
            self._required.update(extra)
        super().__init__(
            datefmt = datefmt,
            exclude_fields = exclude_fields,
            extra = extra
        )
    
    def _rename(self, source, ref_dict, keep_keys, drop=True):
        for key in self._required.keys():
            if key in ref_dict.keys():
                try:
                    source[key] = source[ref_dict.get(key)]
                    if drop: del source[ref_dict.get(key)]
                except KeyError:
                    pass

            # If key already exists, remove the default value
            if key in source.keys():
                try:
                    keep_keys.remove(key)
                except ValueError:
                    pass
        return keep_keys, source

    def format_to_ecs(self, record):

        result = super().format_to_ecs(record)
        result = ecs_logging._utils.flatten_dict(result)

        # rename the result
        default_keys = list(self._required.keys())
        default_keys, result = self._rename(result, ref_dict=self._rename_field, keep_keys=default_keys, drop=True)

        # Copy fields from result
        default_keys, result = self._rename(result, ref_dict=self._copy_field, keep_keys=default_keys, drop=False)

        result.update({key: self._required[key] for key in default_keys})
        return ecs_logging._utils.normalize_dict(result)


class SlackNotification():
    def __init__(self, webhook: Any = None, DEV:bool = True):
        self._dev = os.getenv('DEV', DEV)
        if webhook is None:
            warnings.warn("Using a default slack channel", stacklevel=2)
            webhook = 'https://hooks.slack.com/services/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'
        self._webhook = webhook

    def notify(self, message):
        if not self._dev:
            try:
                from slack_sdk import WebhookClient
            except ImportError:
                warnings.warn("You are in development mode. \nSet $DEV=True", stacklevel=2)
                pass
            try:
                webhook = WebhookClient(self._webhook)
                response = webhook.send(
                    text="custom trigger",
                    blocks=[
                        {   
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "Code Anomaly :expressionless:",
                                "emoji": True
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Type:*\nWebhook trigger"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Timestamp:*\n{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}'
                                }
                            ]
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "plain_text",
                                "text": f"*Message*\n{message}"
                            }
                        }
                    ]
                )
            except Exception as err:
                warnings.warn(f'Need a webhook to send a message \n {err}', stacklevel=2)
                pass
