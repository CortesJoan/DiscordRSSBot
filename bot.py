import os
import discord
from discord.ext import commands, tasks
from rss_feed import RSSFeed
from firebase_service import FirebaseService
import re

class RssBot:
    interval = int(os.environ.get("INTERVAL"))

    def __init__(self, client):
        self.client = client
        self.rss_feed = RSSFeed(self)  # Pass the bot instance to RSSFeed
        self.firebase_service = FirebaseService()
        self.channel_ids = self.load_channel_ids()

        @self.client.hybrid_command(name="ping", description="Test the bot's responsiveness.")
        async def ping(ctx):
            await ctx.send("pong!")

        @self.client.hybrid_command(name="addchannel", description="Add a channel to receive tweets.")
        async def add_channel(ctx, channel: discord.TextChannel):
            if channel is None:
                    await ctx.send(f"Please provide a valid channel")
                    return
            self.channel_ids.append(channel.id)
            os.environ['CHANNEL_IDS'] = str(self.channel_ids)
            await ctx.send(f"Channel id {channel.id} added!")

        @self.client.hybrid_command(name="removechannel", description="Remove a channel from receiving tweets.")
        async def remove_channel(ctx, channel_id: int):
            if channel_id is None:
                    await ctx.send(f"Please provide a valid channel")
                    return
            if channel_id in self.channel_ids:
                self.channel_ids.remove(channel_id)
                os.environ['CHANNEL_IDS'] = str(self.channel_ids)
                await ctx.send(f"Channel id {channel_id} removed!")
            else:
                await ctx.send(f"Channel id {channel_id} is not in the list of channels!")
 
        @self.client.hybrid_command(name='startrss', description="Start the task of fetching and sending tweets.")
        async def start_rss(ctx):
            try:
                self.send_rss.start()
                await ctx.send("RSS task has been started.")
            except RuntimeError as e:
                if str(e) == "Task is already started":
                    await ctx.send("RSS task is already running.")
                else:
                    raise e

        @self.client.hybrid_command(name='pauserss', description="Pause the tweet fetching and sending task.")
        async def pause_rss(ctx):
            self.send_rss.cancel()
            await ctx.send("RSS task has been paused.")
        @self.client.hybrid_command(name='restartrss', description="Restart the tweet fetching and sending task.")
        async def restart_rss(ctx):
            self.send_rss.cancel()
            await ctx.send("Restarting task")
            self.send_rss.start()
            await ctx.send("RSS task has been restarted.")
        @self.client.hybrid_command(name='getrss', description="Retrieve specific tweets (e.g., !getrss 0-5 or !getrss 3).")
        async def get_rss_entry(ctx, range_str: str = None):
            try:
                feed_entries = self.rss_feed.get_feed_entries()
                if range_str is None:
                    await ctx.send(f"Please provide a range in the format 'start-end' (e.g., 0-5). or an individual number like 1")
                else:
                    if(range_str.__contains__('-')):
                        start, end = map(int, range_str.split('-'))
                        if start < 0 or end >= len(feed_entries) or start > end:
                            await ctx.send("Invalid range. Please provide a valid range in the format 'start-end'.")
                        else:
                            
                            for i in range(end, start - 1, -1):
                                entry = feed_entries[i]
                                await ctx.send(self.rss_feed.refine_entry(entry))
                    else:
                        index = int(range_str)
                        if index < 0 or index >= len(feed_entries):
                            await ctx.send("Invalid index. Please provide a valid index.")
                        else:
                            entry = feed_entries[index]
                            await ctx.send(self.rss_feed.refine_entry(entry))
            except Exception as e:
                print("Error while retrieving RSS entry: ", e)
                await ctx.send("An error occurred while retrieving the RSS entry.")
        @self.client.hybrid_command(name='getallrss',description= "Get all rss from the last rss ")
        async def get_all_rss_entry(ctx):
            try:
                feed_entries = self.rss_feed.get_feed_entries()
                for entry in feed_entries:
                    await ctx.send(self.rss_feed.refine_entry(entry))
            except Exception as e:
                print("Error while retrieving RSS entry: ", e)
                await ctx.send("An error occurred while retrieving the RSS entry.")
        @self.client.hybrid_command(name='forcesend',description= "Force the sending of the newest tweets")
        async def force_send(ctx):
            print("Forcing send")
            self.send_rss();

    
    def load_channel_ids(self):
        channel_id_env = os.environ.get("CHANNEL_IDS")
        if channel_id_env:
            return [int(id.strip()) for id in channel_id_env.split(",")]
        else:
            return []

    async def on_ready(self):
        try:
            synced = await self.client.tree.sync()
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(e)

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
                    for i in range(len(new_messages) - 1, -1, -1):
                        new_message = new_messages[i]
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
      
      
        def convert_to_mudae_command(names):
            command = "$topip " + " ".join([f"${name}" for name in names])
            return command

        @self.client.hybrid_command(name="mudae", description="Convert a list of names to a Mudae command.")
        async def mudae(ctx, *, names: str):
            name_list = names.split(',')
            name_list = [name.strip() for name in name_list]  # Clean whitespace
            mudae_command = convert_to_mudae_command(name_list)
            await ctx.send(mudae_command)