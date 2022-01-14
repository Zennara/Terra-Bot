import discord
import os
import keep_alive
from replit import db
import requests
import random
import asyncio
import json

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

guild_ids = [806706495466766366]

invites = {}

#api limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

async def error(message, code):
  embed = discord.Embed(color=0xff0000, description=code)
  await message.channel.send(embed=embed)

def checkPerms(message):
  if message.author.guild_permissions.manage_guild:
    return True
  else:
    asyncio.create_task(error(message, "You do not have the valid permission: `MANAGE_GUILD`."))

def find_invite_by_code(invite_list, code): 
  # loop through invite list
  for invite in invite_list:
    # Check if the invite code in this element of the list is the one we're looking for  
    if invite.code == code:       
      return invite





@bot.slash_command(guild_ids=guild_ids)
async def ping(ctx):
  await ctx.respond("Pong!")




@bot.event
async def on_ready():
  print(f"{bot.user.name} Online.")
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="minecraft"))

  for guild in bot.guilds:
    invites[guild.id] = await guild.invites()

@bot.event
async def on_message(message):
  DUMP = True
  if DUMP:
    data2 = {}
    count = 0
    for key in db.keys():
      data2[str(key)] = db[str(key)]
      count += 1

    with open("database.json", 'w') as f:
      json.dump(str(data2), f)

@bot.event
async def on_member_join(member):  
  #set invites before
  before = invites[member.guild.id]
  #get current invites
  after = await member.guild.invites()
  #loop through invites
  for invite in before: 
    #check if invite went up
    if invite.uses < find_invite_by_code(after, invite.code).uses:
      #set gotinvite
      gotInvite = invite
      print(f"Member {member.name} Joined")
      print(f"Invite Code: {invite.code}")
      print(f"Inviter: {invite.inviter}")
      break
  #reset invites
  invites[member.guild.id] = after

@bot.event
async def on_member_remove(member):
  pass

@bot.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "i/", "iroles":{}}
  #write cache
  invites[guild.id] = await guild.invites()

@bot.event
async def on_invite_create(invite):
  #write cache
  invites[invite.guild.id] = await invite.guild.invites()

@bot.event
async def on_invite_delete(invite):
  #write cache
  invites[invite.guild.id] = await invite.guild.invites()


  
keep_alive.keep_alive()  
bot.run(os.environ.get("TOKEN"))