from discord.ext import commands
import random as rng
from discord.ext.commands import Cog


class RNG(Cog):
    """Utilities that provide pseudo-RNG."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def random(self, ctx):
        """ !help random for more info """
        if ctx.invoked_subcommand is None:
            await self.bot.say('Incorrect random subcommand passed.')

    @random.command(pass_context=True)
    async def tag(self, ctx):
        """Displays a random tag.

        A tag showing up in this does not get its usage count increased.
        """
        tags = self.bot.get_cog('Tags')
        if tags is None:
            await self.bot.say('Tags cog is not loaded.')
            return

        db = tags.get_possible_tags(ctx.message.server)
        name = rng.sample(list(db), 1)[0]
        await self.bot.say('Random tag found: {}\n{}'.format(name, db[name]))
        del tags

    @random.command()
    async def number(self, minimum=0, maximum=100):
        """Displays a random number within an optional range.

        The minimum must be smaller than the maximum and the maximum number
        accepted is 1000.
        """

        maximum = min(maximum, 1000)
        if minimum >= maximum:
            await self.bot.say('Maximum is smaller than minimum.')
            return

        await self.bot.say(rng.randint(minimum, maximum))

    @random.command()
    async def lenny(self):
        """Displays a random lenny face."""
        lenny = rng.choice([
            "( ͡° ͜ʖ ͡°)", "( ͠° ͟ʖ ͡°)", "ᕦ( ͡° ͜ʖ ͡°)ᕤ", "( ͡~ ͜ʖ ͡°)",
            "( ͡o ͜ʖ ͡o)", "͡(° ͜ʖ ͡ -)", "( ͡͡ ° ͜ ʖ ͡ °)﻿", "(ง ͠° ͟ل͜ ͡°)ง",
            "ヽ༼ຈل͜ຈ༽ﾉ"
        ])
        await self.bot.say(lenny)

    @commands.command()
    async def choose(self, *choices):
        """Chooses between multiple choices.

        To denote multiple choices, you should use double quotes.
        """
        if len(choices) < 2:
            await self.bot.say('Not enough choices to pick from.')
        else:
            await self.bot.say(rng.choice(choices))

def setup(bot):
    bot.add_cog(RNG(bot))
