from discord.ext import commands
from .utils import config, checks
from collections import Counter
import re
import discord
import asyncio
from discord.ext.commands import Cog

class Mod(Cog):
    """Moderation related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('mod.json', loop=bot.loop)

    def bot_user(self, message):
        return message.server.me if message.channel.is_private else self.bot.user

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def ignore(self, ctx):
        """!help ignore for more info

        To use these commands, you must have the Bot Admin role or have
        Manage Channel permissions. These commands are not allowed to be used
        in a private message context.

        Users with Manage Roles or Bot Admin role can still invoke the bot
        in ignored channels.
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid subcommand passed: {0.subcommand_passed}'.format(ctx))

    @ignore.command(name='channel', pass_context=True)
    async def channel_cmd(self, ctx):
        """Ignores a specific channel from being processed.

        If no channel is specified, the current channel is ignored.
        If a channel is ignored then the bot does not process commands in that
        channel until it is unignored.
        """
        channel = ctx.message.channel

        ignored = self.config.get('ignored', [])
        if channel.id in ignored:
            await self.bot.say('That channel is already ignored.')
            return

        ignored.append(channel.id)
        await self.config.put('ignored', ignored)
        await self.bot.say('\U0001f44c')

    @ignore.command(name='all', pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _all(self, ctx):
        """Ignores every channel in the server from being processed.

        This works by adding every channel that the server currently has into
        the ignore list. If more channels are added then they will have to be
        ignored by using the ignore command.

        To use this command you must have Manage Server permissions along with
        Manage Channel permissions. You could also have the Bot Admin role.
        """

        ignored = self.config.get('ignored', [])
        channels = ctx.message.server.channels
        ignored.extend(c.id for c in channels if c.type == discord.ChannelType.text)
        await self.config.put('ignored', list(set(ignored))) # make unique
        await self.bot.say('\U0001f44c')

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def unignore(self, ctx):
        """Unignores a specific channel from being processed.

        If no channel is specified, it unignores the current channel.

        To use this command you must have the Manage Channel permission or have the
        Bot Admin role.
        """
        channel = ctx.message.channel

        # a set is the proper data type for the ignore list
        # however, JSON only supports arrays and objects not sets.
        ignored = self.config.get('ignored', [])
        try:
            ignored.remove(channel.id)
        except ValueError:
            await self.bot.say('Channel was not ignored in the first place.')
        else:
            await self.bot.say('\U0001f44c')

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def prunebot(self, ctx, search : int = 100):
        """Cleans up the bot's messages from history.

        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions, then it will try to delete
        messages that look like they invoked the bot as well.

        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count.

        To use this command you must have Manage Messages permission or have the
        Bot Mod role.
        """

        channel = ctx.message.channel
        prefixes = self.bot.command_prefix

        def is_possible_command_invoke(m):
            valid_call = any(m.content.startswith(prefix) for prefix in prefixes)
            return valid_call and not m.content[1:2].isspace()

        def is_me(m):
            return m.author == self.bot.user

        perms = channel.permissions_for(channel.server.me)
        if perms.manage_messages:
            predicate = lambda m: is_me(m) or is_possible_command_invoke(m)
        else:
            predicate = is_me

        deleted = await self.bot.purge_from(channel, limit=search, check=predicate, before=ctx.message)
        spammers = Counter(m.author.display_name for m in deleted)
        reply = await self.bot.say('Clean up completed, {} message(s) were removed'.format(len(deleted)))
        spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
        stats = '\n'.join(map(lambda t: '- **{0[0]}**: {0[1]}'.format(t), spammers))
        await self.bot.whisper(stats)
        await asyncio.sleep(3)
        await self.bot.delete_message(reply)

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def ignoreuser(self, *, member : discord.Member):
        """Bans a user from using the bot.

        Note that this ban is **global**. So they are banned from
        all servers that they access the bot with. So use this with
        caution.

        To use this command you must have the Manage Server permission
        or have a Bot Admin role.
        """

        plonks = self.config.get('plonks', [])
        if member.id in plonks:
            await self.bot.say('That user is already bot banned.')
            return

        plonks.append(member.id)
        await self.config.put('plonks', plonks)
        await self.bot.say('{0.name} has been banned from using the bot.'.format(member))

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def unignoreuser(self, *, member : discord.Member):
        """Unbans a user from using the bot.

        To use this command you must have the Manage Server permission
        or have a Bot Admin role.
        """

        plonks = self.config.get('plonks', [])

        try:
            plonks.remove(member.id)
        except ValueError:
            pass
        else:
            await self.config.put('plonks', plonks)
            await self.bot.say('{0.name} has been unbanned from using the bot.'.format(member))

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def colour(self, ctx, colour : discord.Colour, *, role : discord.Role):
        """Changes the colour of a role.

        The colour must be a hexadecimal value, e.g. FF2AEF. Don't prefix it
        with a pound (#) as it won't work. Colour names are also not supported.

        To use this command you must have the Manage Roles permission or
        have the Bot Mod role or higher. The bot must also have Manage Roles permissions.

        This command cannot be used in a private message.
        """
        try:
            await self.bot.edit_role(ctx.message.server, role, colour=colour)
        except discord.Forbidden:
            await self.bot.say('The bot must have Manage Roles permissions to use this.')
        else:
            await self.bot.say('\U0001f44c')

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def prune(self, ctx, limit : int):
        """Removes x amount of messages.

        In order to use this command, you must have Manage Messages permissions
        or have the Bot Admin role. Note that the bot needs Manage Messages as
        well. These commands cannot be used in a private message.
        """
        message = ctx.message
        deleted = await self.bot.purge_from(message.channel, limit=limit, before=message)
        spammers = Counter(m.author.display_name for m in deleted)
        reply = await self.bot.say('{} messages(s) were removed.'.format(sum(spammers.values())))
        await asyncio.sleep(3)
        await self.bot.delete_message(reply)


    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def remove(self, ctx):
        """Removes messages that meet a criteria.

        In order to use this command, you must have Manage Messages permissions
        or have the Bot Admin role. Note that the bot needs Manage Messages as
        well. These commands cannot be used in a private message.

        When the command is done doing its work, you will get a private message
        detailing which users got removed and how many messages got removed.
        """

        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid criteria passed "{0.subcommand_passed}"'.format(ctx))

    async def do_removal(self, message, limit, predicate):
        deleted = await self.bot.purge_from(message.channel, limit=limit, before=message, check=predicate)
        spammers = Counter(m.author.display_name for m in deleted)
        reply = await self.bot.say('{} message(s) were removed'.format(len(deleted)))
        spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
        stats = '\n'.join(map(lambda t: '**{0[0]}**: {0[1]}'.format(t), spammers))
        await self.bot.whisper(stats)
        await asyncio.sleep(3)
        await self.bot.delete_message(reply)

    @remove.command(pass_context=True)
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx.message, search, lambda e: len(e.embeds))

    @remove.command(pass_context=True)
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx.message, search, lambda e: len(e.attachments))

    @remove.command(pass_context=True)
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx.message, search, lambda e: len(e.embeds) or len(e.attachments))

    @remove.command(name='all', pass_context=True)
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx.message, search, lambda e: True)

    @remove.command(pass_context=True)
    async def user(self, ctx, member : discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx.message, search, lambda e: e.author == member)

    @remove.command(pass_context=True)
    async def contains(self, ctx, *, substr : str):
        """Removes all messages containing a substring.

        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await self.bot.say('The substring length must be at least 3 characters.')
            return

        await self.do_removal(ctx.message, 100, lambda e: substr in e.content)

def setup(bot):
    bot.add_cog(Mod(bot))