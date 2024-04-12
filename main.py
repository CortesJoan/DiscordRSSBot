import os
import discord
from discord.ext import commands
from test_bot import TestBot
from bot import FigurasBot
from keep_alive import keep_alive

def main():
    intents = discord.Intents.all()
    bot = FigurasBot(intents=intents)
    bot.run()

if __name__ == "__main__":
    keep_alive()
    main()