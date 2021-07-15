import asyncio
import discord
import logging

from random import choice
from .utils.utils import json_io_load, json_io_dump
from discord.ext.commands import Cog
from discord.ext import tasks, commands


class BotStatus(Cog):
    """ Switches the now playing status """
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger()
        self.json_file = 'games.json'
        self.games = None
        self._update_games_list()
        self.change_game.start()

    def cog_unload(self):
        """ Unloads the cog """
        self.change_loop.cancel()

    def _add_game_to_games(self, game):
        """ Adds the game to the self.games list and refresh the games list """
        try:
            games = self.games
            games.append(game)
            json_io_dump(self.json_file, games)
            self._update_games_list()
            return True
        except Exception as e:
            self.log.error('Error adding game to games list! {}'.format(e))
            return False

    def _remove_game_to_games(self, game):
        """ Removes the game to the self.games list and refresh the games list """
        try:
            games = self.games
            games.remove(game)
            json_io_dump(self.json_file, games)
            self._update_games_list()
            return True
        except Exception as e:
            self.log.error('Error removing game from games list! {}'.format(e))
            return False

    def _update_games_list(self):
        """ Updates the game list """
        self.games = json_io_load(self.json_file)

    @tasks.loop(minutes=2)
    async def change_game(self):
        """ Changes the game that the bot is playing

        self.games determines the list of games to choose from
        """
        try:
            game = discord.Game(choice(self.games))
            self.log.debug('Changing presence to: {}'.format(game))
            await self.bot.change_presence(activity=game)
        except Exception as e:
            self.log.error('Error switching games: {}'.format(e))
            pass

    @change_game.before_loop
    async def before_change_game(self):
        """ We want to wait until the bot is ready before going into the loop """
        await self.bot.wait_until_ready()

    @commands.group()
    async def status(self, ctx):
        """ Commands to influence status of bot. See !help status for subcommands """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid status command passed... This requires a subcommand')

    @status.command()
    async def change(self, ctx, *, message: str):
        """ Changes the status of the bot

        For example:
            !status change I'm changing this game now

        Will result with the bot changing it's status to:
            Playing I'm changing this game now
        """
        game = discord.Game(message)
        try:
            await self.bot.change_presence(activity=game)
            await ctx.send('Changed bot status to \'{}\'!'.format(message))
        except Exception as e:
            self.log.error('Unable to change game manually: {}'.format(e))
            await ctx.send('Unable to change the bot\'s presence due to some unforseen error.')

    @status.command()
    async def add(self, ctx, *, message: str):
        """ Adds the given query to the possible games played """
        if self._add_game_to_games(message):
            await ctx.send('Added {} to games list!'.format(message))
        else:
            await ctx.send('Unable to add {} to games list...'.format(message))

    @status.command()
    async def remove(self, ctx, *, message: str):
        """ Tries to remove the given query in the games played list """
        if self._remove_game_to_games(message):
            await ctx.send('Removed {} from games list!'.format(message))
        else:
            await ctx.send('Unable to remove *{}* from games list because it was not found!'.format(message))

    @status.command()
    async def show(self, ctx):
        """ Returns all the available games that Jukebot can change status to """
        await ctx.send(self.games)


def setup(bot):
    bot.add_cog(BotStatus(bot))
