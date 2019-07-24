![alt text][pypi_version] ![alt text][licence_version]

# Alerting

Easy to use alerting library for Python 3+

Tested with:
* Python 3.6+

Use the following command to install using pip:
```
pip install alerting
```

## Sample

```python
from alerting import Alerting
from alerting.clients import AlertingMailGunClient, AlertingSlackClient, AlertingTelegramClient

alerts = Alerting(
  clients=[
    AlertingSendGridClient(sendgrid_api_key, from_email),
    AlertingMailGunClient(your_mailgun_api_key, your_domain, from_email, target_email),
    AlertingSlackClient(your_bot_user_oauth, target_channel),
    AlertingTelegramClient(bot_token, chat_id)
  ]
)


try:
  # something
except Exception as ex:
  alerting.send_alert(title='some bad error happened', message=str(ex))

```


[pypi_version]: https://img.shields.io/pypi/v/alerting.svg "PYPI version"
[licence_version]: https://img.shields.io/badge/license-MIT%20v2-brightgreen.svg "MIT Licence"
