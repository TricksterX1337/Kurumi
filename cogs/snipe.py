import discord
from discord.ext import commands

class snipe(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.deleted_messages = {}
        self.edited_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        self.deleted_messages[message.channel.id] = {
            "author": message.author,
            "content": message.content,
            "timestamp": message.created_at,
            "reference": message.reference,
            "channel": message.channel
        }

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        self.edited_messages[before.channel.id] = {
            "author": before.author,
            "before": before.content,
            "after": after.content,
            "timestamp": before.created_at,
            "channel": before.channel
        }

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx, target: str = "deleted"):
        if target.lower() not in ["deleted", "delete", "edit", "edited"]:
            await ctx.message.reply(
                "Invalid target. Use 'delete' or 'edit'.",
                mention_author=True,
                delete_after=10
            )
            return

        if target.lower() == "deleted":
            deleted_message = self.deleted_messages.get(ctx.channel.id)
            if not deleted_message:
                await ctx.message.reply(
                    "There's no deleted message to snipe!",
                    mention_author=True,
                    delete_after=10
                )
                return

            embed = discord.Embed(
              title=f"🚮** Message sent by {deleted_message['author'].mention} deleted in** {deleted_message['channel'].mention}",
                description=f"**__Content__:**\n{deleted_message['content']}",
                timestamp=deleted_message["timestamp"],
                color=discord.Color.teal()
            )
            embed.set_thumbnail(url=deleted_message['author'].display_avatar.url)
            embed.set_footer(text=f"Deleted {deleted_message['timestamp'].strftime('%-d %b %Y %H:%M:%S')}")
            embed.add_field(name="**Deleted by**", value=f"{deleted_message['author'].mention} (ID: {deleted_message['author'].id})", inline=False)

            if deleted_message["reference"] and deleted_message["reference"].resolved:
                replied_to = deleted_message["reference"].resolved.author
                embed.add_field(name="**Replying to...**", value=f'[{deleted_message["reference"].resolved.author}(https://discord.com/users/{deleted_message["reference"].resolved.author.id})', inline=False)

            await ctx.send(embed=embed)

        elif target.lower() in ["edit", "edited"]:
            edited_message = self.edited_messages.get(ctx.channel.id)
            if not edited_message:
                await ctx.message.reply(
                    "There's no edited message to snipe!",
                    mention_author=True,
                    delete_after=5
                )
                return

            embed = discord.Embed(
              title=f"♻️ **Message edited by {edited_message['author'].mention} in** {edited_message['channel'].mention}",
                description=f"**__Before__:**\n{edited_message['before']}\n\n**__After__:**\n{edited_message['after']}",
                timestamp=edited_message["timestamp"],
                color=discord.Color.teal()
            )
            embed.set_thumbnail(url=edited_message['author'].display_avatar.url)
            embed.set_footer(text=f"Edited {edited_message['timestamp'].strftime('%-d %b %Y %H:%M:%S')}")

            await ctx.send(embed=embed)

def setup(client):
  client.add_cog(snipe(client))
