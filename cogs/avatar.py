import discord
from discord.ext import commands

class avatar(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client


def setup(client):
  client.add_cog(avatar(client))
