import keep_alive
import discord
import os
import time
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check
import feedparser
import re
import asyncio
from keep_alive import keep_alive
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
from flask import redirect
from urllib.parse import quote
import uuid

interval = 10 # change this to the number of seconds between each check
emote_to_put_at_message_start = "<:Yossixhehe:1109926657613103154>"
pattern = (r"twitter.com", "fxtwitter.com" ) # change this to the (old, new) strings to replace
last_link = ""
last_message = None
rss_base_domains = "https://nitter.privacydev.net", "https://nitter.poast.org"
rss_account = "/hobbyfiguras/rss"   
channel_ids = []  

intents = discord.Intents.all()
client = commands.Bot(command_prefix='loli', intents=intents) #put your own prefix here

cred_object = credentials.Certificate('./serviceAccountKey.json')
firebase_admin.initialize_app(cred_object, {
    'databaseURL': 'https://botfiguras-default-rtdb.europe-west1.firebasedatabase.app/'
})  # Replace this with your database URL

ref = db.reference('/')

# Crear los nodos si no existen
if not ref.child("last_message").get():
    ref.child("last_message").set({})

if not ref.child("sent_links").get():
    ref.child("sent_links").set({})

bot_data_ref = ref.child("last_message")
sent_links_ref = ref.child("sent_links")

@client.event
async def on_ready():
    print("bot online" )
    # Retrieve channel IDs from environment variables
    channel_id_env = os.environ.get("CHANNEL_IDS")
    if channel_id_env:
        global channel_ids
        channel_ids = [int(id.strip()) for id in channel_id_env.split(",")]
        print(f"Channel IDs loaded from environment variables: {channel_ids}")
    else:
        print("No channel IDs found in environment variables.")
    
    send_rss.start()

@client.command()
async def ping(ctx):
    await ctx.send( "pong!" )

async def kick(ctx, member: discord.Member):
    try:
        await member.kick(reason=None)
        await ctx.send( "kicked " + member.mention )
    except:
        await ctx.send("bot does not have the kick members permission!")

@client.command()
async def addchannel(ctx, channel: discord.TextChannel):
    global channel_ids
    channel_ids.append(channel.id)
    await ctx.send(f"Channel id {channel.id} added!" )

@client.command()
async def removechannel(ctx, channel_id: int):
    global channel_ids
    if channel_id in channel_ids:
        channel_ids.remove(channel_id)
        await ctx.send(f"Channel id {channel_id} removed!" )
    else:
        await ctx.send( f"Channel id {channel_id} is not in the list of channels!" )

@client.command(name="command_nam", description="command_description")
async def unique_command_name(interaction: discord.Interaction):
    print("Done")

@client.tree.command()
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message( f'{first_value} + {second_value} = {first_value + second_value}')
 
@tasks.loop(seconds=interval)
async def send_rss():
    print("Time to check")
    global last_message
    global last_link
    new_messages = prepare_new_rss()
    if new_messages:
        for channel_id in channel_ids:
            channel = client.get_channel(channel_id)
            if channel is not None:
                for new_message in new_messages:
                    link = new_message["link"]
                    if not sent_links_ref.child(str(uuid.uuid4())).get():  # Generate a unique ID for the link
                        print("New content to send")
                        await channel.send(new_message["message"])
                        print("Message sent")
                        sent_links_ref.child(str(uuid.uuid4())).set(link)  # Store the link with the unique ID
                    else:
                        print("No new content to send")
            else:
                print(f"Could not find channel with ID {channel_id}")
        last_message = new_messages[-1]["message"]
        last_link = new_messages[-1]["link"]
        save_last_message(last_message)
        save_last_link(last_link)
        print(last_message)
    else:
        print("No new messages to send")
    await asyncio.sleep(interval)

 

def prepare_new_rss():
    new_messages = []
    try:
        for rss_base_domain in rss_base_domains:
            final_url = rss_base_domain + rss_account
            feed = feedparser.parse(final_url)
            if feed.entries:
                sent_links_data = sent_links_ref.get()
                sent_links = [link for link in sent_links_data.values()] if sent_links_data else []
                for entry in feed.entries:
                    link = entry.link
                    base_domain_pattern = re.escape(rss_base_domain)
                    link = re.sub(base_domain_pattern, 'https://fxtwitter.com', link)
                    if link not in sent_links:
                        message = f"🧸| {entry.title}\n{link}"
                        message = re.sub(r'<[^>]*>', '', message)
                        message = re.sub("🧸", emote_to_put_at_message_start, message)
                        message = re.sub("@Hobbyfiguras: ", '', message)
                        new_messages.append({"message": message, "link": link})
                
                # Update sent_links with new links
                for new_message in new_messages:
                    sent_links_ref.push().set(new_message["link"])
    except Exception as e:
        print("Error while parsing RSS feed: ", e)
    return new_messages

def save_last_message(message):
    global last_link
    bot_data_ref.update({"last_message": message})

def save_last_link(link):
    bot_data_ref.update({"last_link": link})

def load_last_message():
    return bot_data_ref.child("last_message").get() or ""


def load_last_link():
    return bot_data_ref.child("last_link").get() or ""

keep_alive()
last_message = load_last_message()
last_link = load_last_link()
print("the saved message" + last_message + "with link: " + last_link)
client.run(os.environ.get("TOKEN"))
 