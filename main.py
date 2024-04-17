import os
import discord
from discord.ext import commands
from bot import RssBot
from keep_alive import keep_alive
from dotenv import load_dotenv

def main():
    intents = discord.Intents.all()
    load_dotenv()
    client = commands.Bot(command_prefix=os.environ.get('COMMAND_PREFIX'), intents=intents)
    bot = RssBot(client)
    bot.run()
if __name__ == "__main__":
    keep_alive()
    main()