import discord
import os
from discord.ext import commands
from discord.ext.commands.errors import BotMissingAnyRole, BotMissingPermissions
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]
discordtoken = data["DISCORD_TOKEN"]
prefix = data["PREFIX"]

cluster = MongoClient(dbtoken)

intents = discord.Intents.all()
client = commands.Bot(command_prefix = prefix, intents=intents, help_command = None)

#Setup Connections
try:
   cluster.admin.command('ismaster')
   print('[*] Connected to the database.')
except ConnectionFailure:
   print('[*] Connection to the database has failed.')

@client.listen()
async def on_ready():
    print('[*] Connected to discord as: {}'.format(client.user.name))

#Cog Commands
@client.command()
async def load(ctx, extension):
    try:
        client.load_extension(f'cogs.{extension}')
        await ctx.send('Loaded all extensions.', delete_after = 60.0)
    except Exception as e:
        await ctx.send('Something went wrong while loading the extensions: %s' % e, delete_after = 60.0)

@client.command()
async def unload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
        await ctx.send('Unloaded all extensions.', delete_after = 60.0)
    except Exception as e:
        await ctx.send('Something went wrong while unloading the extensions: %s' % e, delete_after = 60.0)

@client.command()
async def reload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send('Reloaded all extensions.', delete_after = 60.0)
    except Exception as e:
        await ctx.send('Something went wrong while reloading the extensions: %s' % e, delete_after = 60.0)

#Load Extensions
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

#Load all the sub-folders
#* Skills
#! Make a for loop
for filename in os.listdir('cogs/skills'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.skills.{filename[:-3]}')

#* Misc
for filename in os.listdir('cogs/misc'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.misc.{filename[:-3]}')

#* Economy
for filename in os.listdir('cogs/economy'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.economy.{filename[:-3]}')

#* Profile
for filename in os.listdir('cogs/profile'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.profile.{filename[:-3]}')

#Catch errors
@client.listen()
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**[*]** You are missing a required argument for this command.")
        return
"""    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**[*]** You do not have the appropriate permissions to run this command.")
        return
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("**[*]** I do not have sufficient permissions!")
        return
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("**[*]** This command is on cooldown for you!")
        return
    else:
        print(f"Error not caught: {error}")"""

client.run(discordtoken)