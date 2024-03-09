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

interval = 10  # change this to the number of seconds between each check
emote_to_put_at_message_start = "<:Yossixhehe:1109926657613103154>"
pattern = (r"twitter\.com", "fxtwitter.com"
           )  # change this to the (old, new) strings to replace
last_link = ""
last_message = None
rss_base_domain = "https://nitter.privacydev.net/"
rss_account = "/hobbyfiguras/rss"
#"https://nitter.uni-sonia.com/Hobbyfiguras/rss"  # change this to your RSS feed URL
channel_ids = [1059813170589479016, 1072888000507285524,1189005278797115472
               ]  # change this to your channel ID





intents = discord.Intents.all()
client = commands.Bot(command_prefix='loli',
                      intents=intents)
                      #put your own prefix here
cred_object = credentials.Certificate('./serviceAccountKey.json')
firebase_admin.initialize_app(cred_object, {
    'databaseURL': 'https://botfiguras-default-rtdb.europe-west1.firebasedatabase.app/'}) # Replace this with your database URL
ref = db.reference('/')
bot_data_ref = ref.child("last_message")

@client.event
async def on_ready():
  print("bot online"
        )  #will print "bot online" in the console when the bot is online
  send_rss.start()


@client.command()
async def ping(ctx):
  await ctx.send(
      "pong!"
  )  #simple command so that when you type "!ping" the bot will respond with "pong!"


async def kick(ctx, member: discord.Member):
  try:
    await member.kick(reason=None)
    await ctx.send(
        "kicked " + member.mention
    )  #simple kick command to demonstrate how to get and use member mentions
  except:
    await ctx.send("bot does not have the kick members permission!")


@client.command()
async def addchannel(ctx, channel: discord.TextChannel):
  global channel_ids  # use the global variable
  channel_ids.append(channel.id)  # add the channel id to the list
  await ctx.send(f"Channel id {channel.id} added!"
                 )  # send a confirmation message


@client.command()
async def removechannel(ctx, channel_id: int):
  global channel_ids  # use the global variable
  if channel_id in channel_ids:
    channel_ids.remove(channel_id)  # remove the channel id from the list
    await ctx.send(f"Channel id {channel_id} removed!"
                   )  # send a confirmation message
  else:
    await ctx.send(
        f"Channel id {channel_id} is not in the list of channels!"
    )  # send an error message if the channel id is not in the list


@client.command(name="command_nam", description="command_description")
async def unique_command_name(interaction: discord.Interaction):
  print("Done")


@client.tree.command()
async def add(interaction: discord.Interaction, first_value: int,
              second_value: int):
  """Adds two numbers together."""
  await interaction.response.send_message(
      f'{first_value} + {second_value} = {first_value + second_value}')


@tasks.loop(seconds=interval)
async def send_rss():
  print("Time to check")
  global last_message
  global last_link
  new_message = last_message
  for channel_id in channel_ids:  # iterate over the channel IDs
    channel = client.get_channel(
        channel_id)  # get the discord channel for each ID
    if channel is not None:  # check if the channel is valid
      new_message = prepare_specific_rss(0)
      if last_link != bot_data_ref.get()["last_link"]:
        print("Messages are not the same")
        await channel.send(new_message)  # send the message to the channel
        print("Message sended")
      else:
        print("No new content to send")

    else:  # handle the error
      print(f"Could not find channel with ID {channel_id}")
  last_message = new_message
  save_last_message(last_message)
  

  print(last_message)
  await asyncio.sleep(interval)


@client.command()
async def force_rss_get(ctx, number: int):
  for channel_id in channel_ids:  # iterate over the channel IDs
    channel = client.get_channel(
        channel_id)  # get the discord channel for each ID
    if channel is not None:  # check if the channel is valid
      new_message = prepare_specific_rss(number)
      await channel.send(new_message)  # send the message to the channel
      print("Message sended")
    else:  # handle the error
      print(f"Could not find channel with ID {channel_id}")


def prepare_specific_rss(number: int):
  global last_link
  global last_message
  message = last_message
  try:
    final_url= rss_base_domain+rss_account
    feed = feedparser.parse(final_url)   
    if feed.entries:   
        if 0 <= number < len(feed.entries):  # validate the number
          latest = feed.entries[number]  # get the latest entry
          link = latest.link  # get the link
          print(f"Link before substitution: {link}")
          print(f"Pattern: {rss_base_domain}")    
          base_domain_pattern = re.escape(rss_base_domain)
          link = re.sub(base_domain_pattern, 'https://fxtwitter.com', link)
          print(f"Link after substitution: {link}")

          last_link=link    
          message = f"🧸| **{latest.title}**\n{link}"
          message = re.sub(r'<[^>]*>', '', message)
          message = re.sub("🧸", emote_to_put_at_message_start, message)
          message = re.sub("@Hobbyfiguras: ", '', message)
      #    message = re.sub(rss_url, 'https://fxtwitter.com',                    message)
    return message
  except URLError as e:
    print("Error while parsing RSS feed: ", e)
    return message

 
# Add this code at the end of your main.py file
def save_last_message(message):
    global last_link
    bot_data_ref.update({"last_message": message})
    bot_data_ref.update({"last_link": last_link})



def load_last_message():
 return bot_data_ref.get()["last_message"]


# run the bot with your token
keep_alive()
last_message = load_last_message()
last_link= bot_data_ref.get()["last_link"]
print("the saved message"+last_message + "with link: " + last_link)
client.run(
    os.environ.get("TOKEN")
)