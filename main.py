import os
import discord
from discord.ext import commands
from bot import FigurasBot
from keep_alive import keep_alive

def main():
    intents = discord.Intents.all()
   # bot = FigurasBot(intents=intents)
    #bot.run()
    bot = TestBot()
    bot.run(os.environ.get('TOKEN'))
if __name__ == "__main__":
    keep_alive()
    main()