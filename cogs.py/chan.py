import discord
from discord.ext import commands, tasks
import asyncio
from typing import Optional

class chan(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.locks = {}  # Store locked channels with unlock time

    @staticmethod
    def parse_time(time_str: str) -> int:
        """Convert time string (e.g., '10s', '5m', '2h') into seconds."""
        units = {"s": 1, "m": 60, "h": 3600}
        try:
            unit = time_str[-1]
            if unit not in units:
                return 0
            return int(time_str[:-1]) * units[unit]
        except (ValueError, IndexError):
            return 0

    async def toggle_channel_lock(self, channel: discord.TextChannel, lock: bool):
        """Lock or unlock a channel by modifying permissions."""
        overwrite = channel.overwrites_for(channel.guild.default_role)
        overwrite.send_messages = None if not lock else False
        await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)
        return lock

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: Optional[discord.TextChannel] = None, duration: Optional[str] = None):
        """Locks the specified channel or the current one."""
        channel = channel or ctx.channel  # Use the provided channel or the current one
        lock_time = self.parse_time(duration) if duration else None

        # Lock the channel
        await self.toggle_channel_lock(channel, lock=True)

        # Send a message indicating the channel is locked (but don't reply to the command directly)
        await channel.send(f"✅️ | {channel.mention} has been locked for everyone role.", mention_author=False)

        if lock_time:
            self.locks[channel.id] = lock_time
            await asyncio.sleep(lock_time)
            if self.locks.get(channel.id) == lock_time:  # Check if lock time hasn't been overridden
                await self.unlock_channel(channel)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Unlocks the specified channel or the current one."""
        channel = channel or ctx.channel
        await self.unlock_channel(channel)

    async def unlock_channel(self, channel: discord.TextChannel):
        """Unlock the channel and remove from the locks list."""
        await self.toggle_channel_lock(channel, lock=False)
        self.locks.pop(channel.id, None)
        # Send a message indicating the channel is unlocked
        await channel.send(f"✅️ | {channel.mention} has been unlocked for everyone role.", mention_author=False)

def setup(client):
    client.add_cog(chan(client))
