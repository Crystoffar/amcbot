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

@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)

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