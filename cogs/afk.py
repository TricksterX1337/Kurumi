import os
import json
import discord
import asyncio
import datetime
from discord.ext import commands
from datetime import datetime, timezone, timedelta

if not os.path.exists('afk.json'):
  with open('afk.json', 'w') as f:
    json.dump({}, f)


def load_afk_data():
  with open('afk.json', 'r') as f:
    return json.load(f)


def save_afk_data(data):
  with open('afk.json', 'w') as f:
    json.dump(data, f, indent=4)


def get_time_difference(start_time):
    now = datetime.now(timezone.utc)
    diff = now - start_time
    minutes, seconds = divmod(diff.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return int(days), int(hours), int(minutes), int(seconds)

def format_duration(days, hours, minutes, seconds):
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return " and ".join(parts)


class afk(commands.Cog):

  def __init__(self, client: commands.Bot):
    self.client = client

  @commands.command()
  async def afk(self, ctx, *, reason: str = "I am AFK :3"):
    user_id = str(ctx.author.id)
    afk_data = load_afk_data()
    afk_time = datetime.now(timezone.utc).isoformat()

    afk_data[user_id] = {'reason': reason, 'time': afk_time}
    save_afk_data(afk_data)

    await ctx.reply(
        f'**{ctx.author.display_name}**, Your AFK is now set to: {reason}', mention_author=False)

  @commands.Cog.listener()
  async def on_message(self, message):

    if message.content.startswith('.afk'):
      return
      await self.client.process_commands(message)


    if message.author.bot:
      return

    user_id = str(message.author.id)
    afk_data = load_afk_data()

    if user_id in afk_data:
      afk_info = afk_data[user_id]
      afk_time = datetime.fromisoformat(afk_info['time'])
      days, hours, minutes, seconds = get_time_difference(afk_time)
      del afk_data[user_id]
      save_afk_data(afk_data)
      duration = format_duration(days, hours, minutes, seconds)
      await message.reply(
          f"**Welcome Back <@{user_id}>!** | You were away for {duration}.",
          mention_author=False)

    for mention in message.mentions:
      mention_id = str(mention.id)
      if mention_id in afk_data:
        afk_info = afk_data[mention_id]
        afk_time = datetime.fromisoformat(afk_info['time'])
        days, hours, minutes, seconds = get_time_difference(afk_time)
        duration = format_duration(days, hours, minutes, seconds)
        await message.reply(
            f'{mention.name} is AFK: {afk_info["reason"]}. They have been AFK for {duration}',
            mention_author=False)

      await self.client.process_commands(message)


def setup(client):
  client.add_cog(afk(client))
