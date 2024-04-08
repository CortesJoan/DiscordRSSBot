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

MAX_SENT_LINKS = 100  # Número máximo de enlaces enviados a mantener en memoria

interval = 10 # change this to the number of seconds between each check
emote_to_put_at_message_start = "<:Yossixhehe:1109926657613103154>"
pattern = (r"twitter.com", "fxtwitter.com" ) # change this to the (old, new) strings to replace
last_link = ""
last_message = None
rss_base_domain = "https://nitter.privacydev.net"
rss_account = "/hobbyfiguras/rss" #"https://nitter.uni-sonia.com/Hobbyfiguras/rss" # change this to your RSS feed URL
channel_ids = [1059813170589479016, 1072888000507285524,1189005278797115472 ] # change this to your channel ID

intents = discord.Intents.all()
client = commands.Bot(command_prefix='loli', intents=intents) #put your own prefix here

cred_object = credentials.Certificate('./serviceAccountKey.json')
firebase_admin.initialize_app(cred_object, {
    'databaseURL': 'https://botfiguras-default-rtdb.europe-west1.firebasedatabase.app/'
})  # Replace this with your database URL

ref = db.reference('/')
bot_data_ref = ref.child("last_message")

@client.event
async def on_ready():
    print("bot online" )
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
    global sent_links
    new_messages = prepare_new_rss()
    if new_messages:
        for channel_id in channel_ids:
            channel = client.get_channel(channel_id)
            if channel is not None:
                for new_message in new_messages:
                    if new_message["link"] not in sent_links:
                        print("New content to send")
                        await channel.send(new_message["message"])
                        print("Message sent")
                        sent_links.append(new_message["link"])
                        if len(sent_links) > MAX_SENT_LINKS:
                            sent_links.pop(0)  # Eliminar el enlace más antiguo
                    else:
                        print("No new content to send")
            else:
                print(f"Could not find channel with ID {channel_id}")
        last_message = new_messages[-1]["message"]
        last_link = new_messages[-1]["link"]
        save_last_message(last_message)
        save_last_link(last_link)
        print(last_message)
    await asyncio.sleep(interval)

@client.command()
async def force_rss_get(ctx, number: int):
    for channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        if channel is not None:
            new_message = prepare_specific_rss(number)
            await channel.send(new_message)
            print("Message sent")
        else:
            print(f"Could not find channel with ID {channel_id}")

def prepare_new_rss():
    global last_link
    global last_message
    new_messages = list()
    try:
        final_url = rss_base_domain + rss_account
        feed = feedparser.parse(final_url)
        if feed.entries:
            for entry in feed.entries:
                link = entry.link
                base_domain_pattern = re.escape(rss_base_domain)
                link = re.sub(base_domain_pattern, 'https://fxtwitter.com', link)
                if link != last_link:
                    message = f"🧸| {entry.title}\n{link}"
                    message = re.sub(r'<[^>]*>', '', message)
                    message = re.sub("🧸", emote_to_put_at_message_start, message)
                    message = re.sub("@Hobbyfiguras: ", '', message)
                    new_messages.append({"message": message, "link": link})
                else:
                    break
        else:
            print("There are no entries on this feed")
    except URLError as e:
        print("Error while parsing RSS feed: ", e)
    return new_messages

def prepare_specific_rss(number: int):
    global last_link
    global last_message
    message = last_message
    try:
        final_url = rss_base_domain + rss_account
        feed = feedparser.parse(final_url)
        if feed.entries:
            if 0 <= number < len(feed.entries):
                latest = feed.entries[number]
                link = latest.link
                print(f"Link before substitution: {link}")
                print(f"Pattern: {rss_base_domain}")
                base_domain_pattern = re.escape(rss_base_domain)
                link = re.sub(base_domain_pattern, 'https://fxtwitter.com', link)
                print(f"Link after substitution: {link}")
                last_link = link
                message = f"🧸| {latest.title}\n{link}"
                message = re.sub(r'<[^>]*>', '', message)
                message = re.sub("🧸", emote_to_put_at_message_start, message)
                message = re.sub("@Hobbyfiguras: ", '', message)
            else:
                print("There are no entries on this feed")
        else:
            print("There are no entries on this feed")
    except URLError as e:
        print("Error while parsing RSS feed: ", e)
    return message

def save_last_message(message):
    global last_link
    bot_data_ref.update({"last_message": message})

def save_last_link(link):
    bot_data_ref.update({"last_link": link})

def load_last_message():
    return bot_data_ref.get()["last_message"]

def load_last_link():
    return bot_data_ref.get()["last_link"]

# Inicializar la lista sent_links en el inicio del bot
sent_links  = list()

# Cargar los enlaces enviados anteriormente desde Firebase
def load_sent_links():
    sent_links_data = bot_data_ref.get("sent_links", [])
    return sent_links_data[:MAX_SENT_LINKS]  # Limitar a los últimos MAX_SENT_LINKS enlaces

# Guardar los enlaces enviados en Firebase
def save_sent_links(sent_links):
    bot_data_ref.update({"sent_links": sent_links})

# Cargar los enlaces enviados anteriormente al iniciar el bot
sent_links = load_sent_links()

# Guardar los enlaces enviados al salir del bot
@client.event
async def on_disconnect():
    save_sent_links(sent_links)

keep_alive()
last_message = load_last_message()
last_link = load_last_link()
print("the saved message" + last_message + "with link: " + last_link)
client.run(os.environ.get("TOKEN"))