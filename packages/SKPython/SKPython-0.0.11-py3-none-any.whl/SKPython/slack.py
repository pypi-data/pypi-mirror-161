import requests
from datetime import datetime as dt

class SlackAlert:
    def __new__(cls, url: str, username: str, channel: str, icon_emoji: str = ":siren:"):
        if not hasattr(cls, "instance"):
            cls.instance = super(SlackAlert, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, url: str, username: str, channel: str, icon_emoji: str = ":siren:"):
        self.url = url
        self.username = username
        self.channel = channel
        self.icon_emoji = icon_emoji

    def send_msg(self, text, alert_user_names, is_channel_alert = False, url = None, channel = None, username = None, icon_emoji = None):
        current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        send_text = ''
        if is_channel_alert:
            send_text += '<!channel>\n'
        if len(alert_user_names) > 0:
            send_text += ",".join(list(map(lambda name: f"<@{name}>", alert_user_names))) + "\n"
                
        send_text += f'[{current_time}] {text}'
        payload = {
            "channel": self.channel if channel is None else channel,
            "username": self.username if username is None else username,
            "text" : send_text,
            "icon_emoji": self.icon_emoji if icon_emoji is None else icon_emoji
        }
        requests.post(self.url if url is None else url, json=payload)

__client__: SlackAlert = None

def init(url: str, username: str, channel: str, icon_emoji: str = ":siren:") -> SlackAlert:
    global __client__
    if __client__ is None:
        __client__ = SlackAlert(url, username, channel, icon_emoji)
    return __client__

def send(text, *alert_user_names, is_channel_alert = False, url = None, channel = None, username = None, icon_emoji = None):
    __client__.send_msg(text, alert_user_names, is_channel_alert, url, channel, username, icon_emoji)