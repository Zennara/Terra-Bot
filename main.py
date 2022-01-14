import discord
import os
import keep_alive
from replit import db
import requests
import random
import asyncio
import json
from discord import Option
from discord.ext import commands

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

guild_ids = [761036747504484392]

invs = {}

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

def resetDB(guild):
  db[str(guild.id)] = {"iroles":{}, "users":{}}
  #guild - [iroles, users]
  #users format - [invites,leaves,code,inviter]

def checkGuild(guild):
  if str(guild.id) not in db:
    resetDB(guild)





@bot.slash_command(description="Ping the bot",guild_ids=guild_ids)
async def ping(ctx):
  await ctx.respond("Pong!")

@bot.slash_command(description="Clear the database",guild_ids=guild_ids)
async def clear(ctx):
  for key in db:
    del key
  resetDB(ctx.guild)
  await ctx.respond("Database cleared")

@bot.slash_command(description="Check your invites",guild_ids=guild_ids)
async def invites(ctx, user:Option(discord.Member, "user to check invites", required=False, default=None)):
  #get user or author
  if user == None:
    user = ctx.author
  #set default values
  full = 0
  leaves = 0
  totalInvites = 0
  #check if in db
  if str(user.id) in db[str(user.guild.id)]["users"]:
    #get full invites
    full = db[str(user.guild.id)]["users"][str(user.id)][0]
    leaves = db[str(user.guild.id)]["users"][str(user.id)][1]
    totalInvites = full - leaves
  #make embed
  embed = discord.Embed(color=0x00FF00,description=f"User has **{totalInvites}** invites! (**{full}** regular, **-{leaves}** leaves)")
  embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
  #reply message
  await ctx.respond(embed=embed)



@bot.event
async def on_ready():
  print(f"{bot.user.name} Online.")
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="minecraft"))

  for guild in bot.guilds:
    invs[guild.id] = await guild.invites()
    checkGuild(guild)

@bot.event
async def on_message(message):
  checkGuild(message.guild)
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
  checkGuild(member.guild)
  #set invites before
  before = invs[member.guild.id]
  #get current invites
  after = await member.guild.invites()
  #loop through invites
  for invite in before: 
    #check if invite went up
    if invite.uses < find_invite_by_code(after, invite.code).uses:
      #set gotinvite
      print(f"Member {member.name} Joined")
      print(f"Invite Code: {invite.code}")
      print(f"Inviter: {invite.inviter}")
      #add to db if they arent in it
      if str(invite.inviter.id) not in db[str(member.guild.id)]["users"]:
        db[str(member.guild.id)]["users"][str(invite.inviter.id)] = [0,0,"",0]
      if str(member.id) not in db[str(member.guild.id)]["users"]:
        db[str(member.guild.id)]["users"][str(member.id)] = [0,0,"",0]
      #add to invites
      db[str(member.guild.id)]["users"][str(invite.inviter.id)][0] += 1
      #add code to joiner
      db[str(member.guild.id)]["users"][str(member.id)][2] = invite.code
      db[str(member.guild.id)]["users"][str(member.id)][3] = invite.inviter.id
      break
  #reset invites
  invs[member.guild.id] = after

@bot.event
async def on_member_remove(member):
  checkGuild(member.guild)
  pass

@bot.event
async def on_guild_join(guild):
  checkGuild(guild)
  #write cache
  invs[guild.id] = await guild.invites()

@bot.event
async def on_invite_create(invite):
  checkGuild(invite.guild)
  #write cache
  invs[invite.guild.id] = await invite.guild.invites()

@bot.event
async def on_invite_delete(invite):
  checkGuild(invite.guild)
  #write cache
  invs[invite.guild.id] = await invite.guild.invites()


  
keep_alive.keep_alive()  
bot.run(os.environ.get("TOKEN"))