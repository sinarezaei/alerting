from . import AlertingClient
from typing import List, Union
import requests
from slackclient import SlackClient


class AlertingSlackClient(AlertingClient):

    def __init__(self, bot_user_oauth: str, target_channel: str):
        assert bot_user_oauth is not None, 'Null bot user oauth provided for slack client'
        assert target_channel is not None, 'Null channel provided for slack client'
        super().__init__()
        self.bot_user_oauth = bot_user_oauth
        self.target_channel = target_channel
        self.slack_client = SlackClient(bot_user_oauth)

    def send_alert(self, message: str):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=self.target_channel,
            text=message
        )


class MailGunClient(AlertingClient):

    def __init__(self, api_key: str, from_email: str, target_email: Union[str,List[str]]):
        assert api_key is not None, 'Null api key passed for MailGun Client'
        assert isinstance(api_key, str), 'Invalid api key passed for MailGun Client, needed str but found ' + str(type(api_key))
        assert from_email is not None, 'Null from email passed for MailGun Client'
        assert isinstance(from_email, str), 'Invalid from email passed for MailGun Client, needed str but found ' + str(type(from_email))
        assert target_email is not None, 'Null target email passed for MailGun Client'
        assert isinstance(target_email, str) or isinstance(target_email, list), 'Invalid target email passed for MailGun client, needed str but found ' + str(type(from_email))
        if isinstance(target_email, list):
            for target in target_email:
                assert isinstance(target, str), 'Invalid email passed to MailGun Client, needed str but found ' + str(type(target))
        super().__init__()
        self.api_key = api_key
        self.from_email = from_email
        self.target_email = target_email

    def send_alert(self, message: str):
        return requests.post(
            "https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages",
            auth=("api", "YOUR_API_KEY"),
            data={"from": self.from_email,
                  "to": self.target_email if isinstance(self.target_email, list) else [self.target_email],
                  "subject": "Alert",
                  "text": message})

