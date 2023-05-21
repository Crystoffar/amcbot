# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
import sqlite3

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
@commands.has_permissions(administrator=True)
async def trackAdd(interaction: discord.Interaction, member: discord.Member, entries, cd):
    '''(ADMIN ONLY) Adds user to tracker'''
    user = member.id
    guild = member.guild
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO tracker VALUES(?, ?, ?)', (user, entries, cd))
    conn.commit()
    conn.close()
    await guild.system_channel.send(member.name + " added to tracker")

@bot.command()
async def check(ctx):
    '''Checks cooldown/entries of user'''
    user = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT cooldown FROM tracker WHERE userid = ?', (user,))
    row = cur.fetchone()

    if (row is not None) and (int(row[0]) != 0):
        cd = str(row[0])
        await ctx.send(ctx.message.author.name + " is on cooldown for " + cd + " more screenings.")
    else:
        cur.execute('SELECT entries FROM tracker WHERE userid = ?', (user,))
        row = cur.fetchone()
        if row is not None:
            entries = str(row[0])
            await ctx.send(ctx.message.author.name + " has " + entries + " entries.")
            cur.execute('SELECT SUM(entries) FROM tracker')
            totalEntries = cur.fetchone()[0]
            await ctx.send("You have a " + '{:.1%}'.format(int(entries)/totalEntries) + " chance to win!")

@bot.command()
@commands.has_permissions(administrator=True)
async def createTracker(ctx):
    '''(ADMIN ONLY) creates tracker'''
    print("adding table!")
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE tracker("userid", "entries", "cooldown")')
    conn.commit()
    conn.close()

@bot.command()
async def speech(ctx):
    '''Recites Nicole Kidman's speech'''
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