import os
import discord
from discord.ext import commands
from bot import FigurasBot
from keep_alive import keep_alive

def main():
    intents = discord.Intents.all()
    client = commands.Bot(command_prefix='loli-', intents=intents)
    bot = FigurasBot(client)
    bot.run()

if __name__ == "__main__":
    keep_alive()
    main()