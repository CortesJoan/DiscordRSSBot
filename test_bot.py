import os
import discord
from discord.ext import commands

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='loli-', intents=intents)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

bot.run(os.environ.get('TOKEN'))