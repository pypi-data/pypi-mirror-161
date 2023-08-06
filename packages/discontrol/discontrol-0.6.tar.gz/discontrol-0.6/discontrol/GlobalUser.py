from discontrol.Client import Client
import requests
from discontrol.Http import DiscordRequest


class DirectMessage:

    def __init__(self, MessageId: int, ChannelId: int, client):
        global token
        token = client.token
        self.MessageId = MessageId
        self.ChannelId = ChannelId

        Json = {}
        headers = {"Authorization": f"Bot {token}"}
        Url = f'https://discord.com/api/v9/channels/{self.ChannelId}/messages/{self.MessageId}'
        resp = requests.patch(Url, json=Json, headers=headers).json()
        self.AuthorId = resp['author']['id']
        self.Content = resp['content']

    def Edit(self, NewContent):
        Json = {'content': NewContent}
        headers = {"Authorization": f"Bot {token}"}
        Url = f'https://discord.com/api/v9/channels/{self.ChannelId}/messages/{self.MessageId}'
        Message = requests.patch(Url, json=Json, headers=headers)


class GlobalUser:

    def __init__(self, user_id: int, client: Client):
        self.user_id = user_id

    def get_user_channel_id(self):
        Json = {'recipient_id': self.user_id}
        headers = {"Authorization": f"Bot {token}"}
        Url = f'https://discord.com/api/v9/users/@me/channels'
        Directory = requests.post(Url, json=Json, headers=headers).json()
        id = Directory['id']
        return id

    def send_message(self, content):
        Json = {'recipient_id': self.user_id}
        headers = {"Authorization": f"Bot {token}"}
        Url = f'https://discord.com/api/v9/users/@me/channels'
        Directory = requests.post(Url, json=Json, headers=headers).json()
        id = Directory['id']
        Json = {'content': content}
        headers = {"Authorization": f"Bot {self.client.token}"}
        Url = f'https://discord.com/api/v9/channels/{id}/messages'
        DMChannelRequest = requests.post(Url, json=Json, headers=headers)
        m = DMChannelRequest.json()['id']
        return DirectMessage(m, id, token)

    def block(self):
        Request = DiscordRequest({'type': 2},
                                 f'users/@me/relationships/{self.user_id}',
                                 self.client.token)
        Request.put()

    def unblock(self):
        Request = DiscordRequest({}, f'users/@me/relationships/{self.user_id}',
                                 self.client.token)
        Request.delete()

    def send_friend_request(self):
        Request = DiscordRequest({}, f'users/@me/relationships/{self.user_id}',
                                 self.client.token)
        Request.put()

    def set_note(self, text):
        Request = DiscordRequest({'note': text},
                                 f'users/@me/notes/{self.user_id}',
                                 self.client.token)
        Request.put()

    def block_notifications(self):
        Request = DiscordRequest({
            'channel_overrides': {
                self.get_user_channel_id(): {
                    'muted': True
                }
            }
        })

        Request.patch()

    def unblock_notifications(self):
        Request = DiscordRequest({
            'channel_overrides': {
                self.get_user_channel_id(): {
                    'muted': False
                }
            }
        })

        Request.patch()