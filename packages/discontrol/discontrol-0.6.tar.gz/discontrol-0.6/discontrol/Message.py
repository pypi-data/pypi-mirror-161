import requests
from discontrol.Errors import errors
from discontrol.RequestBad import request_bad
from discontrol.GuildUser import GuildUser


class Message:

    def __init__(self, message_id, channel_id, client):
        self.message_id = message_id
        self.channel_id = channel_id
        self.client = client

        Url = f'https://discord.com/api/v9/channels/{self.channel_id}/messages/{message_id}'
        Headers = {'Authorization': self.client.token}
        Json = {}

        Request = requests.patch(Url, headers=Headers, json=Json)

        Json = Request.json()

        self.id = message_id
        self.content = Json['content']

        Url = f'https://discord.com/api/v9/channels/{self.channel_id}'

        Request = requests.get(Url, headers=Headers)

        # raise errors.NotFound('Message not found')

    def edit(self, new_text):
        Url = f'https://discord.com/api/v9/channels/{self.channel_id}/messages/{self.message_id}'
        Headers = {'Authorization': self.client.token}
        Json = {'content': new_text}

        Request = requests.patch(Url, json=Json, headers=Headers)

        if self.client.show_logs:
            if Request.status_code in request_bad:
                raise errors.FailedToEditMessage(
                    f'Edit message error: {Request.status_code} - ' +
                    Request.json()['message'], Request.status_code)
            else:
                print('[i] Edit message:', Request.status_code)

        return 0

    def delete(self):
        Headers = {'Authorization': self.client.token}
        Url = f'https://discord.com/api/v9/channels/{self.channel_id}/messages/{self.message_id}'
        Request = requests.delete(Url, headers=Headers)

        if self.client.show_logs:
            if Request.status_code in request_bad:
                raise errors.FailedToDeleteMessage(
                    f'Delete message error: {Request.status_code} - ' +
                    Request.json()['message'], Request.status_code)
            else:
                print('[i] Delete message:', Request.status_code)

        return 0

    def reply(self, content):
        Headers = {'Authorization': self.client.token}
        Url = f'https://discord.com/api/v9/channels/{self.channel_id}'

        Channel = requests.get(Url, headers=Headers).json()
        GuildID = Channel['guild_id']

        Json = {
            'content': content,
            'message_reference': {
                'channel_id': self.channel_id,
                'guild_id': GuildID,
                'message_id': self.message_id
            }
        }
        Url = f'https://discord.com/api/v9/channels/{self.channel_id}/messages'

        Request = requests.post(Url, json=Json, headers=Headers)

        if self.client.show_logs:
            if Request.status_code in request_bad:
                raise errors.FailedToSendMessage(
                    f'Reply message error: {Request.status_code} - ' +
                    Request.json()['message'], Request.status_code)
            else:
                print('[i] Replied message:', Request.status_code)

        Json = Request.json()
        return Message(Json['id'], Json['channel_id'], self.client)