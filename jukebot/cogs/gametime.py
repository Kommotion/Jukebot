import logging
import discord
from datetime import datetime
from discord.ext import tasks, commands
from discord.ext.commands import Cog
from cogs.utils.utils import json_io_dump, json_io_load


log = logging.getLogger(__name__)
STATUS = 'status'
TIME_STARTED = 'time_started'
NAME = 'name'
GAMES = 'games'
NONE = 'none'

# Reference JSON
#  {
#      "player_id1": {
#          "status": "a string of status",
#          "time_started": "time_started_current_status",
#          "games":{
#              "COD MW2": "time_played",
#              "Poop": "time_played"
#          }
#      },
#      "player_id2": {
#          "status": "a string of status",
#          "time_started": "time_started_current_status",
#          "games":{
#              "COD MW2": "time_played",
#              "Poop": "time_played"
#          }
#      }
#  }


class TimePlayed(Cog):
    """ Tracks your time played for each status you have had """
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger()
        self.gametime_file = 'gametime.json'
        self.gametime = None
        self.update_time.start()

    async def game_load(self):
        """ Loads games from JSON """
        self.gametime = json_io_load(self.gametime_file)

    async def game_dump(self):
        """ Dumps games to JSON """
        if not json_io_dump(self.gametime_file, self.gametime):
            self.log.critical('Unable to dump JSON file for TimePlayed!')

    def calculate_addition(self, time_started):
        """ Returns whether to add 2 minutes (in seconds) or something less than that

        Time_started is a datetime.datetime string
        """
        converted_time = datetime.strptime(time_started, '%Y-%m-%d %H:%M:%S')
        delta = (datetime.utcnow().replace(microsecond=0) - converted_time).total_seconds()
        return int(delta) if delta < 120 else 120

    async def get_current_gametime(self):
        """ Returns the dictionary of the current players and what they are playing """
        current_gametime = dict()

        for member in set(self.bot.get_all_members()):
            # Initialize the dictionary for this member and set everything to None
            current_gametime[str(member.id)] = dict()
            current_gametime[str(member.id)][NAME] = member.name
            current_gametime[str(member.id)][STATUS] = NONE
            current_gametime[str(member.id)][TIME_STARTED] = NONE
            current_gametime[str(member.id)][GAMES] = dict()

            # If the member is not doing anything, continue
            if not member.activities:
                continue

            # If the member is playing something, then take note of this
            for activity in member.activities:
                if activity.type == discord.ActivityType.playing:
                    # If for some reason this is not None, then we have 2 gaming activities on this member
                    if current_gametime[str(member.id)][STATUS] != NONE:
                        self.log.critical('There are multiple games playing right now in Gametime for single member!')
                        self.log.critical('{} had status {} instead of none as expected.'.format(
                            current_gametime[str(member.id)][NAME], current_gametime[str(member.id)][STATUS]))
                    current_gametime[str(member.id)][STATUS] = activity.name
                    date = member.activity.start.replace(microsecond=0) if member.activity.start else datetime.utcnow().replace(microsecond=0)
                    current_gametime[str(member.id)][TIME_STARTED] = str(date)
                    current_gametime[str(member.id)][GAMES][activity.name] = 0

        return current_gametime

    async def compare_and_update(self, current_gametime):
        """ Compares and updates the playing list """
        for id in current_gametime:
            if id not in self.gametime:
                self.gametime[id] = current_gametime[id]

            current_status = current_gametime[id][STATUS]

            # If the current gametime is not None, then update the time on the game currently played
            if current_status != NONE:
                if current_status not in self.gametime[id][GAMES]:
                    self.gametime[id][GAMES][current_status] = 0
                result = self.calculate_addition(current_gametime[id][TIME_STARTED])
                self.gametime[id][GAMES][current_status] += result

            # If the current game is different from last game, add 2 minutes to the last game
            if current_status != self.gametime[id][STATUS] and self.gametime[id][STATUS] != NONE:
                self.gametime[id][GAMES][self.gametime[id][STATUS]] += 120

            # Update the game status regardless of what's going on
            self.gametime[id][STATUS] = current_gametime[id][STATUS]
            self.gametime[id][TIME_STARTED] = current_gametime[id][TIME_STARTED]

    def calculate_days_minutes_seconds(self, seconds):
        """ Returns the days hours minutes seconds from seconds """
        # years, seconds = seconds // 31556952, seconds % 31556952
        # months, seconds = seconds // 2629746, seconds % 2629746
        days, seconds = seconds // 86400, seconds % 86400
        hours, seconds = seconds // 3600, seconds % 3600
        minutes, seconds = seconds // 60, seconds % 60
        msg = '{:02d} Days, {:02d} Hours, {:02d} Minutes, {:02d} Seconds'.format(days, hours, minutes, seconds)

        if days > 9000:
            msg += ' ITS OVER 9000!'

        if days == 69:
            msg += ' Hah, nice... 69'

        return msg

    @commands.command()
    async def played(self, ctx, *, member: discord.Member = None):
        """Returns the amount of time played for every game

        If Member is not specified, then returns the played information for member that sent command
        """
        if member is None:
            member = ctx.author

        if str(member.id) not in self.gametime:
            await ctx.send('ERROR!: Unable to find {} in gametime list... looks like a bug'.format(member.mention))

        msg = 'Time played for {}\n'.format(member.mention)

        if not self.gametime[str(member.id)][GAMES]:
            msg += '`Looks like {} hasn\'t played any games!`'.format(member.display_name)

        for game in self.gametime[str(member.id)][GAMES]:
            msg += '`{:<30}: {}`\n'.format(game, self.calculate_days_minutes_seconds(self.gametime[str(member.id)][GAMES][game]))

        await ctx.send('{}'.format(msg))

    @tasks.loop(minutes=2)
    async def update_time(self):
        """ Loop that updates the time played of the current game for each member

        Steps:
            1. Load list
            2. Get Current List of people playing
            3. Compare new with old list of people playing and update old gametime list as needed
            4. Write list
        """
        self.log.debug('Starting gametime save loop')

        await self.game_load()
        current_gametime = await self.get_current_gametime()
        await self.compare_and_update(current_gametime)
        await self.game_dump()

        self.log.debug('End gametime save loop')

    @update_time.before_loop
    async def before_update_time(self):
        """ We want to wait until the bot is ready before going into the loop """
        await self.bot.wait_until_ready()

    @update_time.after_loop
    async def after_update_time(self):
        """ If anything is happening after the loop, we want to store all the information before any exits """
        await self.game_dump()


def setup(bot):
    bot.add_cog(TimePlayed(bot))
