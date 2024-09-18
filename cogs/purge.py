import discord
from discord.ext import commands

class purge(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  async def purge_bots(self, ctx, amount):
    def is_bot(message):
        return message.author.bot
    deleted = await ctx.channel.purge(limit=amount, check=is_bot)
    await ctx.send(f'Purged {len(deleted)} messages from bots.', delete_after=5)

  async def purge_members(self, ctx, amount):
      def is_member(message):
        return not message.author.bot
      deleted = await ctx.channel.purge(limit=amount, check=is_member)
      await ctx.send(f'Purged {len(deleted)} messages from members.', delete_after=5)

  async def purge_images(self, ctx, amount):
    def has_image(message):
      return any(attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')) for attachment in message.attachments)
    deleted = await ctx.channel.purge(limit=amount, check=has_image)
    await ctx.send(f'Purged {len(deleted)} image messages.', delete_after=5)

  async def purge_links(self, ctx, amount):
        def has_link(message):
            return 'http' in message.content or 'www' in message.content
        
        deleted = await ctx.channel.purge(limit=amount, check=has_link)
        await ctx.send(f'Purged {len(deleted)} link messages.', delete_after=5)

    
  @commands.command()
  @commands.has_permissions(manage_messages=True)
  async def purge(self, ctx, target=None, amount: int = 100):
    try:
        if target is None:
            await ctx.mmessage.delete()
            await ctx.channel.purge(limit=amount)
            await ctx.send(f'✅️ | Successfully cleared {amount} messages.', delete_after=5)
        elif target.lower() == 'bots':
            await self.purge_bots(ctx, amount)
        elif target.lower() == 'users':
            await self.purge_members(ctx, amount)
        elif target.lower() == 'images':
            await self.purge_images(ctx, amount)
        elif target.lower() == 'links':
            await self.purge_links(ctx, amount)
        elif target.isdigit():
            await ctx.channel.purge(limit=int(target))
        else:
            await ctx.channel.purge(check=lambda m: target in m.content, limit=amount)
            await ctx.send(f'✅️ | Successfully cleared {amount} messages.', delete_after=5)
    except:
                await ctx.send('Invalid target or amount specified.', delete_after=5)


def setup(client):
  client.add_cog(purge(client))
