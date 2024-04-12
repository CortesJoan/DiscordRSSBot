import os
from discord.ext import commands, tasks
from rss_feed import RSSFeed
from firebase_service import FirebaseService

class FigurasBot:
    def __init__(self, client):
        self.client = client
        self.rss_feed = RSSFeed()
        self.firebase_service = FirebaseService()
        self.channel_ids = self.load_channel_ids()
        self.interval = 10

    def run(self):
        self.client.event(self.on_ready)
        self.client.command()(self.ping)
        self.client.command()(self.addchannel)
        self.client.command()(self.removechannel)
        self.send_rss.start()
        self.client.run(os.environ.get("TOKEN"))

    async def on_ready(self):
        print("bot online")

    async def ping(self, ctx):
        await ctx.send("pong!")

    async def addchannel(self, ctx, channel: discord.TextChannel):
        self.channel_ids.append(channel.id)
        await ctx.send(f"Channel id {channel.id} added!")

    async def removechannel(self, ctx, channel_id: int):
        if channel_id in self.channel_ids:
            self.channel_ids.remove(channel_id)
            await ctx.send(f"Channel id {channel_id} removed!")
        else:
            await ctx.send(f"Channel id {channel_id} is not in the list of channels!")

    @tasks.loop(seconds=10)
    async def send_rss(self):
        new_messages = self.rss_feed.get_new_messages()
        if new_messages:
            for channel_id in self.channel_ids:
                channel = self.client.get_channel(channel_id)
                if channel is not None:
                    for new_message in new_messages:
                        await channel.send(new_message["message"])
                        self.firebase_service.save_sent_link(new_message["link"])
                else:
                    print(f"Could not find channel with ID {channel_id}")
            self.firebase_service.save_last_message(new_messages[-1]["message"])
            self.firebase_service.save_last_link(new_messages[-1]["link"])
        else:
            print("No new messages to send")

    def load_channel_ids(self):
        channel_id_env = os.environ.get("CHANNEL_IDS")
        if channel_id_env:
            return [int(id.strip()) for id in channel_id_env.split(",")]
        else:
            return []