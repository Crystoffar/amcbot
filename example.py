# This example requires the 'message_content' intent.

import discord
from discord.ext import commands

description = 'A bot for helping AMC screenings'

#sets intents for bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', description =description, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def speech(ctx):
    with open('speech.txt') as file:
        lines = [line.strip() for line in file]
    speech = ''
    for line in lines:
        speech += line
        speech += '\n'
    await ctx.send(speech)

#loads token from token.txt and saves in token string
with open('token.txt') as file:
    lines = [line.strip() for line in file]
token = lines[0]

bot.run(token)