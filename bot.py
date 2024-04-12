import os
import discord
from discord.ext import commands, tasks
from rss_feed import RSSFeed
from firebase_service import FirebaseService
class FigurasBot:
    interval = 10
    def __init__(self, client):
        self.client = client
        self.rss_feed = RSSFeed()
        self.firebase_service = FirebaseService()
        self.channel_ids = self.load_channel_ids()
    

    def run(self):
        self.client.event(self.on_ready)
        self.client.command(name='addchannel')(self.addchannel)
        self.client.command(name='removechannel')(self.removechannel)
        self.client.command(name='getrssentry')(self.getrssentry)
        self.client.command(name='pauserss')(self.pause_rss)
        self.client.run(os.environ.get("TOKEN"))

    async def on_ready(self):
        self.send_rss.start()
        print("bot online")
    @commands.command()
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

    @tasks.loop(seconds=interval)
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
    async def getrssentry(self, ctx, entry_number: int):
        entry = self.rss_feed.get_entry(entry_number)
        if entry:
            await ctx.send(entry["message"])
        else:
            await ctx.send(f"Entry number {entry_number} not found.")

    @commands.command(name='startrss')
    async def start_rss(self, ctx):
        try:
            self.send_rss.start()
            await ctx.send("RSS task has been started.")
        except RuntimeError as e:
            if str(e) == "Task is already started":
                await ctx.send("RSS task is already running.")
            else:
                raise e

    @commands.command(name='pauserss')
    async def pause_rss(self, ctx):
        self.send_rss.cancel()
        await ctx.send("RSS task has been paused.")