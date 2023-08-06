from discontrol.Errors import errors
from discontrol.Client import Client
from discontrol.Http import DiscordRequest


class Category:

    def __init__(self, CategoryId: int, client: Client):
        pass


class Channel:

    def __init__(self, ChannelId: int, client: Client):
      try:
          http = DiscordRequest({}, f"channels/{ChannelId}", client.token, False)
          request = http.patch()
          rq = request.json()
          self.ChannelId = rq['id']
          self.GuildId = rq['guild_id']
          self.ChannelName = rq['name']
          self.Type = rq['type']
          self.Client = client
          self.Json = rq
          global token
          token = client.token
      except:
        raise errors.InvalidResponse(f'This response invalid -> {rq}')

    def SendMessage(self, Message):
        return self.Client.send_message(self.ChannelId, Message)
