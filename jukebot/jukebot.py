from discord.ext import commands
import discord
from cogs.utils import checks
import datetime, re
import json, asyncio
import copy
import logging
import sys


description = """
Hello! My name is JukeBot! Use '!' as command prefix!
"""

initial_extensions = [
    'cogs.rng',
    'cogs.tags',
    'cogs.gameswitcher',
    'cogs.messagechecker',
    'cogs.gametime',
    'cogs.general'
]
log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='jukebot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(handler)


help_attrs = dict(hidden=True)
bot = commands.Bot(command_prefix=['!'], description=description, pm_help=False, help_attrs=help_attrs)
bot.commands_executed = 0


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')


@bot.event
async def on_ready():
    print('Logged in as:')
    print('Username: ' + bot.user.name)
    print('ID: ' + str(bot.user.id))
    print('-----------------------------')
    bot.uptime = datetime.datetime.utcnow()


@bot.event
async def on_resumed():
    print('resumed...')


@bot.event
async def on_command(ctx):
    bot.commands_executed += 1
    message = ctx.message
    if isinstance(message.channel, discord.abc.PrivateChannel):
        destination = 'Private Message'
    else:
        destination = '#{0.channel.name} ({0.guild.name})'.format(message)

    log.info('{0.created_at}: {0.author.name} in {1}: {0.content}'.format(message, destination))


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)


def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)


if __name__ == '__main__':
    credentials = load_credentials()
    token = credentials['token']
    bot.client_id = credentials['client_id']

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.run(token)

    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)
