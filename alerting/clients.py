from . import AlertingClient
from typing import List, Union
import requests
from slackclient import SlackClient
import sendgrid
from sendgrid.helpers.mail import Content, Mail, Email
from telegram import Bot


class AlertingSlackClient(AlertingClient):

    def __init__(self, bot_user_oauth: str, target_channel: str):
        assert bot_user_oauth is not None, 'Null bot user oauth provided for slack client'
        assert target_channel is not None, 'Null channel provided for slack client'
        super().__init__()
        self.bot_user_oauth = bot_user_oauth
        self.target_channel = target_channel
        self.slack_client = SlackClient(bot_user_oauth)

    def send_alert(self, title: str, message: str):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=self.target_channel,
            text='Title: '+ title + '\n'+message
        )


class AlertingMailGunClient(AlertingClient):

    def __init__(self, api_key: str, domain: str, from_email: str, target_email: Union[str,List[str]]):
        assert api_key is not None, 'Null api key passed for MailGun Client'
        assert isinstance(api_key, str), 'Invalid api key passed for MailGun Client, needed str but found ' + str(type(api_key))
        assert domain is not None, 'Null domain passed for MailGun Client'
        assert isinstance(domain, str), 'Invalid domain passed for MailGun Client, needed str but found ' + str(type(api_key))
        assert from_email is not None, 'Null from email passed for MailGun Client'
        assert isinstance(from_email, str), 'Invalid from email passed for MailGun Client, needed str but found ' + str(type(from_email))
        assert target_email is not None, 'Null target email passed for MailGun Client'
        assert isinstance(target_email, str) or isinstance(target_email, list), 'Invalid target email passed for MailGun client, needed str but found ' + str(type(from_email))
        if isinstance(target_email, list):
            for target in target_email:
                assert isinstance(target, str), 'Invalid email passed to MailGun Client, needed str but found ' + str(type(target))
        super().__init__()
        self.api_key = api_key
        self.domain = domain
        self.from_email = from_email
        self.target_email = target_email

    def send_alert(self, title: str, message: str):
        return requests.post(
            "https://api.mailgun.net/v3/" + self.domain + "/messages",
            auth=("api", self.api_key),
            data={"from": self.from_email,
                  "to": self.target_email if isinstance(self.target_email, list) else [self.target_email],
                  "subject": title,
                  "text": message})


class AlertingSendGridClient(AlertingClient):
    def __init__(self, api_key: str, from_email: str, target_email: str):
        assert api_key is not None, 'Null api key passed for SendGrid Client'
        assert isinstance(api_key, str), 'Invalid api key passed for SendGrid Client, needed str but found ' + str(type(api_key))
        assert from_email is not None, 'Null from email passed for SendGrid Client'
        assert isinstance(from_email, str), 'Invalid from email passed for SendGrid Client, needed str but found ' + str(type(from_email))
        assert target_email is not None, 'Null target email passed for SendGrid Client'
        assert isinstance(target_email, str), 'Invalid target email passed for SendGrid client, needed str but found ' + str(type(from_email))
        super().__init__()
        self.api_key = api_key
        self.from_email = from_email
        self.target_email = target_email

    def send_alert(self, title: str, message: str):
        sg = sendgrid.SendGridAPIClient(
            apikey=self.api_key)
        from_email_ = Email(self.from_email)
        to_email_ = Email(self.target_email)
        content = Content('text/html', message)
        mail = Mail(from_email=from_email_, subject=title, to_email=to_email_, content=content)
        response = sg.client.mail.send.post(request_body=mail.get())


class AlertingTelegramClient(AlertingClient):
    def __init__(self, token: str, chat_id: str):
        assert token is not None, 'Null token passed for Telegram Client'
        assert isinstance(token, str), 'Invalid token passed for Telegram Client, needed str but found ' + str(type(token))
        assert chat_id is not None, 'Null chat id passed for Telegram Client'
        assert isinstance(chat_id, str), 'Invalid chat id passed for Telegram Client, needed str but found ' + str(type(chat_id))
        super().__init__()
        self.token = token
        self.chat_id = chat_id

    def send_alert(self, title: str, message: str):
        telegram_bot = Bot(token=self.token)
        full_message = 'Title: ' + title + '\n' + message
        telegram_bot.send_message(
            chat_id=self.chat_id,
            text=full_message)
