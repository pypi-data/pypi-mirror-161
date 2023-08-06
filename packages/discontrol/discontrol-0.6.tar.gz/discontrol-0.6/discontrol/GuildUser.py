import requests
import datetime


class GuildUserCommands:

    def __init__(self, token: int):
        self.token = token

    def changenick(self, user_id: int, guild_id: int, newnick: str):
        headers = {"Authorization": f"Bot {self.token}"}
        url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
        json = {'nick': newnick}
        response = requests.patch(url, headers=headers, json=json)
        if response.status_code in range(200, 299):
            return True
        else:
            return False

    def timeout(self, user_id: int, guild_id: int, until):
        headers = {"Authorization": f"Bot {self.token}"}
        url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
        timeout = (datetime.datetime.utcnow() +
                   datetime.timedelta(seconds=until)).isoformat()
        json = {'communication_disabled_until': timeout}
        response = requests.patch(url, headers=headers, json=json)

        if response.status_code in range(200, 299):
            return True
        else:
            return False

    def ban(self,
            user_id: int,
            guild_id: int,
            reason: str = "",
            deletemessagesdays: int = 0):
        headers = {"Authorization": f"Bot {self.token}"}
        url = f"https://discord.com/api/v9/guilds/{guild_id}/bans/{user_id}"
        json = {'reason': reason, 'delete_message_days': deletemessagesdays}
        response = requests.patch(url, headers=headers, json=json)
        if response.status_code in range(204):
            return True
        else:
            return False

    def kick(self, user_id: int, guild_id: int, reason: str = ""):
        headers = {"Authorization": f"Bot {self.token}"}
        url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
        json = {'reason': reason}
        response = requests.delete(url, headers=headers, json=json)
        print(response.text)
        if response.status_code in range(204):
            return True
        else:
            return False


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


class GuildUser:

    def __init__(self, Token: int, GuildId: int, UserId: int):
        global token
        token = Token
        headers = {"Authorization": f"Bot {Token}"}
        url = f"https://discord.com/api/v9/guilds/{GuildId}/members/{UserId}"
        json = {}
        response = requests.patch(url, headers=headers, json=json).json()
        self.UserId = UserId
        self.GuildId = GuildId
        self.Commands = GuildUserCommands(Token)
        self.UserName = response['user']['username']
        self.Avatar = response['user']['avatar']
        self.Discriminator = response['user']['discriminator']

    def Kick(self, Reason: str):
        self.Commands.kick(self.UserId, self.GuildId, Reason)

    def Ban(self, Reason: str):
        self.Commands.ban(self.UserId, self.GuildId, Reason)

    def ChangeNickname(self, NewNick: str):
        self.Commands.changenick(self.UserId, self.GuildId, NewNick)

    def SendMessage(self, Message: str):
        global token
        snowflake = self.UserId
        Json = {'recipient_id': self.UserId}
        headers = {"Authorization": f"Bot {token}"}
        Url = f'https://discord.com/api/v9/users/@me/channels'
        DM = requests.post(Url, json=Json, headers=headers).json()
        id = DM['id']
        Json = {'content': Message}
        headers = {"Authorization": f"Bot {token}"}
        Url = f'https://discord.com/api/v9/channels/{id}/messages'
        DMChannelRequest = requests.post(Url, json=Json, headers=headers)
        m = DMChannelRequest.json()['id']
        return DirectMessage(m, id, token)

    def GetRoles(self):
        global token
        headers = {"Authorization": f"Bot {token}"}
        url = f"https://discord.com/api/v9/guilds/{self.GuildId}/members/{self.UserId}"
        json = {}
        response = requests.patch(url, headers=headers, json=json).json()
        return response['roles']

    def UpdateInformation(self):
        global token
        headers = {"Authorization": f"Bot {token}"}
        url = f"https://discord.com/api/v9/guilds/{self.GuildId}/members/{self.UserId}"
        json = {}
        response = requests.patch(url, headers=headers, json=json).json()
        self.UserId = self.UserId
        self.GuildId = self.GuildId
        self.Commands = GuildUserCommands(token)
        self.UserName = response['user']['username']
        self.Avatar = response['user']['avatar']
        self.Discriminator = response['user']['discriminator']

    def GetUserJson(self):
        global token
        headers = {"Authorization": f"Bot {token}"}
        url = f"https://discord.com/api/v9/guilds/{self.GuildId}/members/{self.UserId}"
        json = {}
        response = requests.patch(url, headers=headers, json=json).json()
        return response
