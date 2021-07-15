import discord
import os, datetime
import re, asyncio

from discord.ext import commands
from .utils import checks, formats
from collections import OrderedDict, deque, Counter
from discord.ext.commands import Cog


class General(Cog):
    """Commands for utilities related to Discord or the Bot itself. """

    def __init__(self, bot):
        self.bot = bot

    def _get_bot_uptime(self):
        """ Returns the uptime of the bot """
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, and {s} seconds'

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    def _get_about(self):
        """ Returns the about information """
        result = list()
        result.append('**About Me:**')
        result.append('`- Version : Jukebot 2.0`')
        result.append('`- Author  : Kommotion (ID: 87324314084331520)`')
        result.append('`- Library : discord.py (Python)`')
        result.append('`https://github.com/Rapptz/discord.py`')
        return '\n'.join(result)

    @commands.command()
    async def stats(self, ctx):
        """ Prints out the stats of the bot """
        await ctx.send('To be implemented')

    @commands.command()
    async def uptime(self, ctx):
        """ Prints out how long the bot has been online """
        await ctx.send('Uptime: **{}**'.format(self._get_bot_uptime()))

    @commands.command()
    async def about(self, ctx):
        """ Prints out information about the bot """
        await ctx.send(self._get_about())

    @commands.has_permissions(manage_messages=True)
    @commands.group()
    async def prune(self, ctx, amount: int):
        """ Removes a certain amount of commands """
        if not ctx.invoked_subcommand:
            await ctx.send('To be implemented')

    @prune.command()
    async def juice(self, ctx):
        """ This is some juicy shit """
        await ctx.send('WHAT THE FUCK NIGGA')

    # @commands.command()
    # async def emotes(self):
    #     """Displays all available emotes that JukeBot can upload """
    #     await self.bot.say(checks.get_faces())
    #
    # @commands.command(hidden=True)
    # async def hello(self):
    #     """Says hi back."""
    #     await self.bot.say('Hello! My name is JukeBot!')
    #
    # @commands.command(name='quit', hidden=True)
    # @checks.is_owner()
    # async def _quit(self):
    #     """Quits the bot."""
    #     await self.bot.logout()
    #
    # @commands.command(pass_context=True, no_pm=True, invoke_without_command=True)
    # async def info(self, ctx, *, member: discord.Member = None):
    #     """Shows info about a member.
    #
    #     This cannot be used in private messages. If you don't specify
    #     a member then the info returned will be yours.
    #     """
    #     channel = ctx.message.channel
    #     if member is None:
    #         member = ctx.message.author
    #
    #     roles = [role.name.replace('@', '@\u200b') for role in member.roles]
    #     shared = sum(1 for m in self.bot.get_all_members() if m.id == member.id)
    #     voice = member.voice_channel
    #     if voice is not None:
    #         other_people = len(voice.voice_members) - 1
    #         voice_fmt = '{} with {} others' if other_people else '{} by themselves'
    #         voice = voice_fmt.format(voice.name, other_people)
    #     else:
    #         voice = 'Not connected.'
    #
    #     entries = [
    #         ('Name', member.name),
    #         ('Tag', member.discriminator),
    #         ('ID', member.id),
    #         ('Joined', member.joined_at),
    #         ('Created', member.created_at),
    #         ('Roles', ', '.join(roles)),
    #         ('Servers', '{} shared'.format(shared)),
    #         ('Voice', voice),
    #         ('Avatar', member.avatar_url),
    #     ]
    #
    #     await formats.entry_to_code(self.bot, entries)
    #
    # @commands.command(pass_context=True, no_pm=True)
    # @checks.admin_or_permissions(manage_roles=True)
    # async def botpermissions(self, ctx):
    #     """Shows the bot's permissions.
    #
    #     This is a good way of checking if the bot has the permissions needed
    #     to execute the commands it wants to execute.
    #
    #     To execute this command you must have Manage Roles permissions or
    #     have the Bot Admin role. You cannot use this in private messages.
    #     """
    #     channel = ctx.message.channel
    #     member = ctx.message.server.me
    #     await self.say_permissions(member, channel)
    #
    # def get_bot_uptime(self):
    #     now = datetime.datetime.utcnow()
    #     delta = now - self.bot.uptime
    #     hours, remainder = divmod(int(delta.total_seconds()), 3600)
    #     minutes, seconds = divmod(remainder, 60)
    #     days, hours = divmod(hours, 24)
    #     if days:
    #         fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
    #     else:
    #         fmt = '{h} hours, {m} minutes, and {s} seconds'
    #
    #     return fmt.format(d=days, h=hours, m=minutes, s=seconds)
    #
    # @commands.command()
    # async def join_server(self):
    #     """Shows the invite link to a server."""
    #     msg = 'This link will allow you to give me permissions to join your server\n\n'
    #     perms = discord.Permissions.none()
    #     perms.read_messages = True
    #     perms.send_messages = True
    #     perms.manage_roles = True
    #     perms.ban_members = True
    #     perms.kick_members = True
    #     perms.manage_messages = True
    #     perms.embed_links = True
    #     perms.read_message_history = True
    #     perms.attach_files = True
    #     await self.bot.say(msg + discord.utils.oauth_url(self.bot.client_id, perms))
    #
    # @commands.command(pass_context=True, no_pm=True)
    # @checks.admin_or_permissions(manage_server=True)
    # async def leave(self, ctx):
    #     """Leaves the server.
    #
    #     To use this command you must have Manage Server permissions or have
    #     the Bot Admin role.
    #     """
    #     server = ctx.message.server
    #     try:
    #         await self.bot.leave_server(server)
    #     except:
    #         await self.bot.say('Could not leave..')
    #
    #
    # @commands.command()
    # async def uptime(self):
    #     """Tells you how long the bot has been up for."""
    #     await self.bot.say('Uptime: **{}**'.format(self.get_bot_uptime()))
    #
    # def format_message(self, message):
    #     return 'On {0.timestamp}, {0.author} said {0.content}'.format(message)
    #
    # @commands.command()
    # async def about(self):
    #     """Tells you information about the bot itself."""
    #     result = ['**About Me:**']
    #     result.append('`- Author  : Kommotion (ID: 87324314084331520)`')
    #     result.append('`- Library : discord.py (Python)`')
    #     result.append('`- Credits : Rapptz/Danny for Library and commands extension`')
    #     result.append('`- Credits : Gdraynz for reminder and gametime cog base`')
    #     result.append('`https://github.com/Rapptz/discord.py`')
    #     await self.bot.say('\n'.join(result))
    #
    # @commands.command()
    # async def stats(self):
    #     """Gives bot statistics"""
    #     result = ['General Statistics:']
    #     result.append('`- Uptime: {}`'.format(self.get_bot_uptime()))
    #     result.append('`- Servers: {}`'.format(len(self.bot.servers)))
    #     result.append('`- Commands Run: {}`'.format(self.bot.commands_executed))
    #     # statistics
    #     total_members = sum(len(s.members) for s in self.bot.servers)
    #     total_online  = sum(1 for m in self.bot.get_all_members() if m.status != discord.Status.offline)
    #     unique_members = set(self.bot.get_all_members())
    #     unique_online = sum(1 for m in unique_members if m.status != discord.Status.offline)
    #     channel_types = Counter(c.type for c in self.bot.get_all_channels())
    #     voice = channel_types[discord.ChannelType.voice]
    #     text = channel_types[discord.ChannelType.text]
    #     result.append('`- Total Members: {} ({} online)`'.format(total_members, total_online))
    #     result.append('`- Unique Members: {} ({} online)`'.format(len(unique_members), unique_online))
    #     result.append('`- {} text channels, {} voice channels`'.format(text, voice))
    #     await self.bot.say('\n'.join(result))
    #
    #
    # @commands.command(rest_is_raw=True, hidden=True)
    # @checks.is_owner()
    # async def echo(self, *, content):
    #     """Echoes the user"""
    #     await self.bot.say(content)
    #
    # @commands.command(pass_context=True, no_pm = True)
    # async def avatar(self, ctx, *, member : discord.Member = None):
    #     """Shows an <@mentioned> user's avatar."""
    #
    #     if member is None:
    #         member = ctx.message.author
    #
    #     await self.bot.say(member.avatar_url)
    #
    # @commands.command(pass_context=True, no_pm=True)
    # @checks.admin_or_permissions(create_instant_invite=True)
    # async def invite(self, ctx):
    #     """Creates a temporary invite to the channel
    #
    #     To use this command you must have Create Instant Invite permissions
    #     or have the Bot Admin role.
    #     """
    #     channel = ctx.message.channel
    #
    #     invite = await self.bot.create_invite(channel, max_age=18000)
    #     await self.bot.say(invite.url)
    #
    # @commands.command(pass_context=True)
    # async def calc(self, ctx, *, code : str):
    #     """ Takes in command and tries to process """
    #     code = code.strip('` ')
    #     python = '```py\n{}\n```'
    #     result = None
    #
    #     try:
    #         result = eval(code)
    #     except Exception as e:
    #         await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
    #         return
    #
    #     if asyncio.iscoroutine(result):
    #         result = await result
    #
    #     await self.bot.say(python.format(result))


def setup(bot):
    bot.add_cog(General(bot))
