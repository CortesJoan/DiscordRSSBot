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
if not ref.child("last_message").get():
    ref.child("last_message").set({})

if not ref.child("sent_links").get():
    ref.child("sent_links").set({})
bot_data_ref = ref.child("last_message")
sent_links_ref = ref.child("sent_links")
if not sent_links_ref.get():
    sent_links_ref.set({})
if not bot_data_ref.get():
    bot_data_ref.set({})
if not bot_data_ref.child("last_message").get():
    bot_data_ref.child("last_message").set("")
if not bot_data_ref.child("last_link").get():
    bot_data_ref.child("last_link").set("")
@client.event
async def on_ready():
    print("bot online" )
    # Crear el nodo 'sent_links' si no existe
   
    send_rss.start() 
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
                    if not sent_links_ref.child(link).get():  # Verificar si el enlace ya ha sido enviado
                        print("New content to send")
                        await channel.send(new_message["message"])
                        print("Message sent")
                        sent_links_ref.child(link).set(True)  # Marcar el enlace como enviado
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
# ... (resto del código sin cambios)

def save_last_message(message):
    global last_link
    bot_data_ref.update({"last_message": message})

def save_last_link(link):
    bot_data_ref.update({"last_link": link})

def load_last_message():
    return bot_data_ref.get()["last_message"]


def load_last_link():
    return bot_data_ref.get()["last_link"]


keep_alive()
last_message = load_last_message()
last_link = load_last_link()
print("the saved message" + last_message + "with link: " + last_link)
client.run(os.environ.get("TOKEN"))