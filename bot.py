import os
import discord
from discord.ext import commands, tasks
from rss_feed import RSSFeed
from firebase_service import FirebaseService
import re

class FigurasBot:
    interval = 10

    def __init__(self, client):
        self.client = client
        self.rss_feed = RSSFeed(self)  # Pass the bot instance to RSSFeed
        self.firebase_service = FirebaseService()
        self.channel_ids = self.load_channel_ids()

        @self.client.command("ping")
        async def ping(self):
            await self.send("pong!")

        @self.client.command("addchannel")
        async def addchannel(self, ctx, channel: discord.TextChannel):
            self.channel_ids.append(channel.id)
            await ctx.send(f"Channel id {channel.id} added!")

        @self.client.command("removechannel")
        async def removechannel(self, ctx, channel_id: int):
            if channel_id in self.channel_ids:
                self.channel_ids.remove(channel_id)
                await ctx.send(f"Channel id {channel_id} removed!")
            else:
                await ctx.send(f"Channel id {channel_id} is not in the list of channels!")

        @self.client.command(name='startrss')
        async def start_rss(self, ctx):
            try:
                self.send_rss.start()
                await ctx.send("RSS task has been started.")
            except RuntimeError as e:
                if str(e) == "Task is already started":
                    await ctx.send("RSS task is already running.")
                else:
                    raise e

        @self.client.command(name='pauserss')
        async def pause_rss(self, ctx):
            self.send_rss.cancel()
            await ctx.send("RSS task has been paused.")
        @self.client.command(name='restartrss')
        async def restart_rss(self, ctx):
            self.send_rss.cancel()
            self.send_rss.start()
            await ctx.send("RSS task has been restarted.")
        @self.client.command(name='getrss')
        async def get_rss_entry(self, ctx, index: int = 0):
            try:
                feed_entries = self.rss_feed.get_feed_entries()
                if index is None:
                    await ctx.send(f"Please provide an index between 0 and {len(feed_entries) - 1}.")
                elif 0 <= index < len(feed_entries):
                    entry = feed_entries[index]
                    message = f"🧸| {entry.title}\n{entry.link}"
                    message = re.sub(r'<[^>]*>', '', message)
                    message = re.sub("🧸", self.rss_feed.emote_to_put_at_message_start, message)
                    message = re.sub("@Hobbyfiguras: ", '', message)
                    await ctx.send(message)
                else:
                    await ctx.send(f"Invalid index. Please provide a value between 0 and {len(feed_entries) - 1}.")
            except Exception as e:
                print("Error while retrieving RSS entry: ", e)
                await ctx.send("An error occurred while retrieving the RSS entry.")
                 
    
    def load_channel_ids(self):
        channel_id_env = os.environ.get("CHANNEL_IDS")
        if channel_id_env:
            return [int(id.strip()) for id in channel_id_env.split(",")]
        else:
            return []

    async def on_ready(self):
        self.send_rss.start()
        print("bot online")

    def run(self):
        self.client.event(self.on_ready)
        self.client.run(os.environ.get("TOKEN"))

    @tasks.loop(seconds=interval)
    async def send_rss(self):
        new_messages = self.rss_feed.get_new_messages()
        if new_messages:
            for channel_id in self.channel_ids:
                channel = self.client.get_channel(channel_id)
                if channel is not None:
                    for new_message in new_messages:
                        await channel.send(new_message["message"])
                        self.firebase_service.save_sent_link(
                            new_message["link"])
                else:
                    print(f"Could not find channel with ID {channel_id}")
            self.firebase_service.save_last_message(
                new_messages[-1]["message"])
            self.firebase_service.save_last_link(new_messages[-1]["link"])
        else:
            print("No new messages to send")
