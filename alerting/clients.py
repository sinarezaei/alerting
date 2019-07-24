from . import AlertingClient

import re
import time
import requests
from threading import Thread
from typing import List, Union, Optional

from slackclient import SlackClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from telegram import Bot


class AlertingSlackClient(AlertingClient):

    def __init__(self, bot_user_oauth: str, target_channel: str, user_access_token: Optional[str] = None):
        assert bot_user_oauth is not None, 'Null bot user oauth provided for slack client'
        assert target_channel is not None, 'Null channel provided for slack client'
        super().__init__()
        self.user_access_token = user_access_token
        self.bot_user_oauth = bot_user_oauth
        self.target_channel = target_channel
        self.bot_client = SlackClient(bot_user_oauth)

        if self.user_access_token is not None:
            self.user_client = SlackClient(user_access_token)
            thread = Thread(target=AlertingSlackClient.start_watching, args=(self.bot_client, self.user_client, self.user_access_token, self.target_channel))
            thread.start()

    def send_alert(self, title: str, message: str):
        self.bot_client.api_call(
            "chat.postMessage",
            channel=self.target_channel,
            text='Title: '+ title + '\n'+message
        )

    @staticmethod
    def start_watching(bot_client: SlackClient, user_client: SlackClient, user_access_token: str, target_channel: str):
        RTM_READ_DELAY = 1
        if bot_client.rtm_connect():
            bot_auth_test = bot_client.api_call("auth.test")
            bot_id = bot_auth_test["user_id"]

            user_auth_test = user_client.api_call('auth.test')
            bot_user_id = user_auth_test['user_id']

            def parse_direct_mention(message_text):
                """
                    Finds a direct mention (a mention that is at the beginning) in message text
                    and returns the user ID which was mentioned. If there is no direct mention, returns None
                """
                matches = re.search("^<@(|[WU].+?)>(.*)", message_text)
                # the first group contains the username, the second group contains the remaining message
                return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

            def parse_bot_commands(slack_events):
                """
                    Parses a list of events coming from the Slack RTM API to find bot commands.
                    If a bot command is found, this function returns a tuple of command and channel.
                    If its not found, then this function returns None, None.
                """
                for event in slack_events:
                    if event["type"] == "message" and not "subtype" in event:
                        user_id, message = parse_direct_mention(event["text"])
                        if user_id == bot_id:
                            return message, event["channel"]
                return None, None

            def handle_command(command, channel):
                if command in ['clear', 'clear_channel', 'clear channel']:
                    bot_client.api_call(
                        "chat.postMessage",
                        channel=channel,
                        text='Affirmative, cleaning channel messages...'
                    )

                    # fetch history of messages in channel
                    all_messages_ts = []
                    messages = user_client.api_call(
                        'channels.history',
                        token=user_access_token,
                        channel=channel,
                        count=1000
                    )
                    if messages['ok'] is True:
                        for message in messages['messages']:
                            all_messages_ts.append(message['ts'])
                    for ts in list(reversed(all_messages_ts)):
                        delete_resp = user_client.api_call(
                            'chat.delete',
                            token=user_access_token,
                            channel=channel,
                            ts=ts,
                            as_user=True
                        )
                else:

                    # Sends the default response back to the channel
                    bot_client.api_call(
                        "chat.postMessage",
                        channel=channel,
                        text="Not sure what you mean. Try *clear*."
                    )

            while True:
                command, channel = parse_bot_commands(bot_client.rtm_read())
                if command:
                    handle_command(command, channel)
                time.sleep(RTM_READ_DELAY)
        else:
            print("Connection failed. Exception traceback printed above.")


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
        sg = SendGridAPIClient(api_key=self.api_key)
        message = Mail(
            from_email=self.from_email,
            to_emails=self.target_email,
            subject=title,
            html_content=message)
        response = sg.send(message)
        return response


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
