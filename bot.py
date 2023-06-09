# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
import sqlite3
import random
import pickle
from google_images_search import GoogleImagesSearch
import os

#loads token, api, and cx from token.txt and saves in token string
with open('token.txt') as file:
    lines = [line.strip() for line in file]
token = lines[0]
api = lines[1]
cx = lines[2]

# Set up the Google Images API
gis = GoogleImagesSearch(api, cx)

description = 'A bot for helping AMC screenings'

#sets intents for bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

winnerInfo = 'winner.pk'

bot = commands.Bot(command_prefix='!', description =description, intents=intents)

@bot.event
async def on_ready():
    await bot.add_cog(Admin(bot))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_member_join(member):
    #sets guild to discord server
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)

@bot.command()
async def speech(ctx):
    '''Recites Nicole Kidman's speech'''
    #opens speech.text and loads into lines array
    with open('speech.txt') as file:
        lines = [line.strip() for line in file]
    speech = ''
    #iterates through lines array and saves to speech string
    for line in lines:
        speech += line
        speech += '\n'
    await ctx.send(speech)

@bot.command()
async def chooseMovie(ctx, movieName):
    '''Allows raffle winner to select next movie'''
    #unpickles info from winner.pk
    with open(winnerInfo, 'rb') as fi:
        #info is saved as winner, movie, date
        info = pickle.load(fi)
    
    if(ctx.message.author.id == info[0]):
        #pickles winner with default values
        with open(winnerInfo, 'wb') as fi:
            #info is saved as winner, movie, date
            info = [info[0], movieName, info[2]]
            pickle.dump(info, fi)

        await ctx.send("Okay, the next screening will be " + movieName)
    else:
        await ctx.send("You're not the most recent raffle winner.")


@bot.command()
async def screening(ctx):
    '''Provides information for next screening'''
    #unpickles info from winner.pk
    with open(winnerInfo, 'rb') as fi:
        #info is saved as winner, movie, date
        info = pickle.load(fi)

    if info[0] != None:
        user = await bot.fetch_user(info[0])

    if info[1] != "TBD":
        query = info[1] + "movie poster"

        gis.search({'q': query, 'num': 1})
        results = gis.results()
        if len(results) > 0:
            image = results[0]
            filename = image.url.split('/')[-1]
            image.download('./images')
            with open(f'./images/{filename}', 'rb') as f:
                picture = discord.File(f)
                await ctx.send(file=picture)

            poster = './images/' + filename
            try:
                os.remove(poster)
            except OSError as e:
                print("Error: %s file not found" % poster)
        else:
            await ctx.send("Sorry, I couldn't find any images for that query.")

    if info[0] != None:
        await ctx.send("The next screening will be " + info[1] + " on " + info[2] + " chosen by " + user.name)
    else:
        await ctx.send("The next screening will be " + info[1] + " on " + info[2])

@bot.command()
async def attend(ctx):
    '''Records attendance for going to a screening'''
    user = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    #checks user's cooldown
    cur.execute('SELECT cooldown FROM tracker WHERE userid = ?', (user,))
    row = cur.fetchone()

    #if user has cooldown and it isn't 0
    if (row is not None) and (int(row[0]) != 0):
        cd = str(row[0])
        await ctx.send("Thanks for attending, " + ctx.message.author.name + ", but you are still on cooldown for " + cd + " more screenings.")
    else:
        #increments user's entries by 1
        cur.execute('UPDATE tracker SET entries = entries + 1 WHERE userid = ?', (user,))
        #saves entries to row 
        cur.execute('SELECT entries FROM tracker WHERE userid = ?', (user,))
        row = cur.fetchone()
        #if user is in table, gets entries
        if (row is not None):
            entries = str(row[0])
        else:
            entries = '0'
        await ctx.send("Thanks for attending, " + ctx.message.author.name + ". You now have " + entries + " entries for the next raffle!")

    conn.commit()
    conn.close()

@bot.command()
async def check(ctx):
    '''Checks cooldown/entries of user'''
    user = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    #checks user's cooldown
    cur.execute('SELECT cooldown FROM tracker WHERE userid = ?', (user,))
    row = cur.fetchone()

    #if user has cooldown and it isn't 0
    if (row is not None) and (int(row[0]) != 0):
        cd = str(row[0])
        await ctx.send(ctx.message.author.name + " is on cooldown for " + cd + " more screenings.")
    else:
        #checks user's entries
        cur.execute('SELECT entries FROM tracker WHERE userid = ?', (user,))
        row = cur.fetchone()
        #if user has entries
        if row is not None:
            entries = str(row[0])
            await ctx.send(ctx.message.author.name + " has " + entries + " entries.")
            cur.execute('SELECT SUM(entries) FROM tracker')
            totalEntries = cur.fetchone()[0]
            #calculates percentage based on total entries
            if row[0] != 0:
                await ctx.send("You have a " + '{:.1%}'.format(int(entries)/totalEntries) + " chance to win!")
            else:
                await ctx.send("You have a {:.1%} chance to win!".format(0))
    conn.close()

class Admin(commands.Cog):
    """Commands for Administrators"""
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createTracker(self, ctx):
        '''(ADMIN ONLY) Creates tracker'''
        print("adding table!")
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE tracker("userid", "entries", "cooldown")')
        conn.commit()
        conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def manualScreening(self, ctx, movieName, date):
        '''(ADMIN ONLY) Sets next screening manually'''

        #pickles winner with chosen values
        with open(winnerInfo, 'wb') as fi:
            #info is saved as winner, movie, date
            info = [None, movieName, date]
            pickle.dump(info, fi)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setDate(self, ctx, date):
        '''(ADMIN ONLY) Sets date for next screening'''
        #unpickles info from winner.pk
        with open(winnerInfo, 'rb') as fi:
            #info is saved as winner, movie, date
            info = pickle.load(fi)

        #pickles winner with saved values
        with open(winnerInfo, 'wb') as fi:
            #info is saved as winner, movie, date
            info = [info[0], info[1], date]
            pickle.dump(info, fi)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setWinner(self, ctx, member: discord.Member):
        '''(ADMIN ONLY) Sets chooser for next screening'''
        winner = member.id

        #pickles winner with saved values
        with open(winnerInfo, 'wb') as fi:
            #info is saved as winner, movie, date
            info = [winner, "TBD", "TBD"]
            pickle.dump(info, fi)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setValues(self, interaction: discord.Interaction, member: discord.Member, entries, cd):
        '''(ADMIN ONLY) Manually sets values for user'''
        user = member.id
        guild = member.guild
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('UPDATE tracker SET cooldown = ?, entries = ? WHERE userid = ?', (cd, entries, user))
        conn.commit()
        conn.close()
        await guild.system_channel.send(member.name + " set to entries = " + entries + " cd = " + cd)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addUser(self, interaction: discord.Interaction, member: discord.Member, entries, cd):
        '''(ADMIN ONLY) Adds user to tracker'''
        user = member.id
        guild = member.guild
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('INSERT INTO tracker VALUES(?, ?, ?)', (user, entries, cd))
        conn.commit()
        conn.close()
        await guild.system_channel.send(member.name + " added to tracker")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def decCD(self, ctx):
        '''(ADMIN ONLY) Reduces all cooldowns by 1'''
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        #decrements cooldown for all, if at 0 stay at zero
        cur.execute('UPDATE tracker SET cooldown = MAX(cooldown - 1, 0) WHERE cooldown > 0')

        conn.commit()
        conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def raffle(self, ctx):
        '''(ADMIN ONLY) Raffles for next choice'''
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        # Gets all entries from 
        cur.execute('SELECT userid, entries FROM tracker')
        rows = cur.fetchall()

        raffle_list = []

        # Build the raffle list
        for row in rows:
            userid = row[0]
            entries = int(row[1])
            
            #sets amount of times user is in list based on number of entries
            raffle_list.extend([userid] * entries)

        #randomly chooses from raffle list
        winner = random.choice(raffle_list)

        await ctx.send(f"<@{winner}> has won the raffle!")

        #pickles winner with default values
        with open(winnerInfo, 'wb') as fi:
            #info is saved as winner, movie, date
            info = [winner, "TBD", "TBD"]
            pickle.dump(info, fi)

        #decrements cooldown for all, if at 0 stay at zero
        cur.execute('UPDATE tracker SET cooldown = MAX(cooldown - 1, 0) WHERE cooldown > 0')

        #sets winner's entries to 0 and cooldown to 3
        cur.execute('UPDATE tracker SET entries = 0, cooldown = 3 WHERE userid = ?', (winner,))

        conn.commit()
        conn.close()

bot.run(token)