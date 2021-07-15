import discord
import os
from discord.ext.commands import Cog
from discord.ext import commands


class Emotes(Cog):
    """ Checks messages and does what it needs to do :) """
    def __init__(self, bot):
        self.bot = bot
        self.pics_path = self._get_pics_path()
        self.words = self._get_pics()

    def _get_pics(self):
        """ Returns dictionary with the following key,val being picture name,file type

        For example:
            'LUL': 'png',
        """
        pic_dict = dict()
        pics = os.listdir(self.pics_path)

        for pic in pics:
            temp = pic.split('.')
            pic_name = temp[0]
            pic_extension = temp[1]
            pic_dict[pic_name] = pic_extension

        return pic_dict

    def _get_pics_path(self):
        """ Returns the path to all of the faces """
        script_dir = os.path.dirname(__file__)
        rel_path = os.path.join('utils', 'pics')
        return os.path.join(script_dir, rel_path)

    async def check_message(self, message):
        """
        Checks the message for any possible faces and uploads them if possible
        """
        raw_message = message.clean_content.lower()
        channel = message.channel

        # Check if Duck fevon
        if 'duck fevon' in raw_message:
            msg = 'Duck Fevon Indeed {}!'.format(message.author.mention)
            await channel.send(msg, tts=True)

        # Special jukebot things
        if 'jukebot' in raw_message:
            if 'best' in raw_message or 'amazing' in raw_message:
                await channel.send(file=discord.File(os.path.join(self.pics_path, 'thankyou.gif')))
            if 'ily' in raw_message or '\u2764' in raw_message or 'love' in raw_message:
                await channel.send('\u2764 you too!')

        # Finally, check for the emotes
        data = message.content.strip('\n').split()
        for word in self.words:
            if word in data:
                file_name = word + '.' + self.words[word]
                file = discord.File(os.path.join(self.pics_path, file_name))
                await channel.send(file=file)

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Carries out the checker on the message given """
        if message.author.bot:
            return

        await self.check_message(message)

    @commands.command()
    async def emotes(self, ctx):
        """ Returns a list of the supported emotes

        These emotes can be accessed just by typing in the emote in the chat
        """
        await ctx.send('Supported emotes:\n{}'.format(list(self.words.keys())))


def setup(bot):
    bot.add_cog(Emotes(bot))
