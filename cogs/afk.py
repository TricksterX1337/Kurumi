import os
import json
import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, timedelta

# Ensure 'afk.json' exists
if not os.path.exists('afk.json'):
    with open('afk.json', 'w') as f:
        json.dump({}, f)

# Helper functions to load and save AFK data
def load_afk_data():
    with open('afk.json', 'r') as f:
        return json.load(f)


def save_afk_data(data):
    with open('afk.json', 'w') as f:
        json.dump(data, f, indent=4)


def get_time_difference(start_time):
    """Calculate the difference between now and the start time."""
    now = datetime.now(timezone.utc)
    diff = now - start_time
    days, seconds = divmod(diff.total_seconds(), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return int(days), int(hours), int(minutes), int(seconds)


def format_duration(days, hours, minutes, seconds):
    """Format the duration in a readable way."""
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
        """Command to set AFK status."""
        user_id = str(ctx.author.id)
        afk_data = load_afk_data()
        afk_time = datetime.now(timezone.utc).timestamp()  # Use UNIX timestamp

        # Save reason and timestamp
        afk_data[user_id] = {'reason': reason, 'time': afk_time}
        save_afk_data(afk_data)

        # Confirmation message
        await ctx.reply(
            f'**{ctx.author.display_name}**, Your AFK is now set to: {reason}',
            mention_author=False
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Ensure AFK command is not processed as a regular message
        ctx = await self.client.get_context(message)
        if ctx.valid:  # This checks if the message is a command
            return
        await self.client.process_commands(message)

        # Check if the author is AFK
        user_id = str(message.author.id)
        afk_data = load_afk_data()

        if user_id in afk_data:
            # User is returning from AFK
            afk_info = afk_data.pop(user_id)  # Remove AFK status
            save_afk_data(afk_data)

            afk_time = datetime.fromtimestamp(afk_info['time'], tz=timezone.utc)
            days, hours, minutes, seconds = get_time_difference(afk_time)
            duration = format_duration(days, hours, minutes, seconds)

            await message.reply(
                f"**Welcome Back <@{user_id}>!** | You were away for {duration}.",
                mention_author=False
            )

        # Check if the mentioned users are AFK
        for mention in message.mentions:
            mention_id = str(mention.id)
            if mention_id in afk_data:
                # User is AFK
                afk_info = afk_data[mention_id]
                afk_time = afk_info['time']
                reason = afk_info['reason']

                await message.reply(
                    f'**{mention.display_name}** went afk <t:{int(afk_time)}:R>: {reason}',
                    mention_author=False
                )


def setup(client):
    client.add_cog(afk(client))
