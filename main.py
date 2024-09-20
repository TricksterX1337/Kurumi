import os
import jishaku
import discord
from discord.ext import commands
from websocket import identify
from discord.gateway import DiscordWebSocket, _log
from discord.ext.commands import Bot

from cogs.afk import afk
from cogs.purge import purge
from cogs.snipe import snipe

intents = discord.Intents.all()
intents.messages = True
DiscordWebSocket.identify = identify

client = commands.AutoShardedBot(command_prefix='.', intents=intents)

@client.event
async def on_ready():
  try:
    print(f"Connected to {client.user}")
    await client.load_extension('jishaku')
    await cog_loader()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="yall\'s shenanigans"))
  except Exception as e:
    print(e)


async def cog_loader():
  await client.add_cog(afk(client))
  await client.add_cog(snipe(client))
  await client.add_cog(purge(client)) 

client.run(os.environ['token'])
