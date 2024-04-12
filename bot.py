import discord
from discord.ext import commands

class FigurasBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, command_prefix='loli-', **kwargs)

    async def on_ready(self):
        print("Bot online")

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send("pong!")