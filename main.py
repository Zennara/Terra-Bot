#imports (most required)
#pip install git+https://github.com/Pycord-Development/pycord
#https://discord.com/api/oauth2/authorize?client_id=931431695977181184&permissions=8&scope=bot%20applications.commands
import discord
import os
import keep_alive
from replit import db
import requests
import random
import asyncio
import json
from discord.ext import commands
from discord import Option
from discord.commands import SlashCommandGroup
from datetime import datetime, timedelta
import math

intents = discord.Intents.all()
bot = commands.Bot(intents=intents)

guild_ids = [761036747504484392]

invs = {}

onlineTime = datetime.now()

#api limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

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
  db[str(guild.id)] = {"mod":0, "iroles":{}, "users":{}}
  #guild - [iroles, users]
  #users format - [invites,leaves,code,inviter,bumps]

def checkGuild(guild):
  if str(guild.id) not in db:
    resetDB(guild)

async def error(ctx, code):
  embed = discord.Embed(color=0xFF0000, description= f"❌ {code}")
  await ctx.respond(embed=embed)

def staff(ctx):
  checkGuild(ctx.guild)
  mod = db[str(ctx.guild.id)]["mod"]
  if ctx.author == ctx.guild.owner:
      return True
  if mod != 0:
    if ctx.guild.get_role(mod) <= ctx.author.top_role:
      return True
  return False
  #error response
  #embed = discord.Embed(color=0xFF0000, description= "❌ You do not have permission to use this")
  #ctx.respond(embed=embed)


@bot.slash_command(description="Use me for help!",guild_ids=guild_ids, hidden=True)
async def help(ctx):
  helpText = """
  This bot uses **slash commands**. This mean all bot commands starts with `/`.
  You can find more help in my [Discord server](https://discord.gg/YHHvT5vWnV).

  **Commands**
  `/help` - Displays this message
  `/invites [user]` - Check the invites of a user or yourself
  `/ileaderboard` - View the servers invites leaderboard
  `/invite` - View all your active invites
  """
  if staff(ctx):
    helpText += """
    
    **Staff Commands**
    `/fetch` - Fetch the servers previous invites
    `/edit <invites|leaves> <amount> [member]` - Edit the invites or leaves of a user
    `/addirole <invites> <role>` - Add an invite role reward
    `/delirole <role>` - Delete an invite role reward
    `/iroles` - Display the server's invite role rewards
    """
  embed = discord.Embed(color=0x00FF00,description=helpText)
  embed.set_footer(text="________________________\n<> Required | [] Optional\nMade By Zennara#8377")
  #reply message
  await ctx.respond(embed=embed)


@bot.slash_command(description="Show the bot's uptime",guild_ids=guild_ids)
async def ping(ctx):
  embed = discord.Embed(color=0x00FF00, title="**Pong!**", description=f"{bot.user.name} has been online for {datetime.now()-onlineTime}!")
  await ctx.respond(embed=embed)


@bot.slash_command(description="Clear the database",guild_ids=guild_ids)
async def clear(ctx):
  if staff(ctx):
    for key in db:
      del key
    resetDB(ctx.guild)
    await ctx.respond("Database cleared")
  else:
    await error(ctx, "You do not have the proper permissions to do this")


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


@bot.slash_command(description="Show all of your active invites", guild_ids=guild_ids)
async def invite(ctx):
  if await ctx.guild.invites():
    inviteText = "**Code** \_\_\_\_\_\_\_\_\_\_\_\_ **Uses** \_\_ **Expires in**\n"
    for invite in await ctx.guild.invites():  
      if invite.inviter.id == ctx.author.id:
        dTime = str(timedelta(seconds=invite.max_age))
        if dTime != "0:00:00":
          if "day" in dTime:
            newTime = (dTime[0:6] if dTime.endswith("0:00:00") else dTime[8:]).replace(",","")
          else:
            newTime = dTime
        else:
          newTime = "Never"
        inviteText = inviteText + "`" +invite.code+""+(" "*(15-len(invite.code)))+""+ " | " +str(invite.uses)+ " / " +(str(invite.max_uses) if invite.max_uses != 0 else "∞")+ " | " + newTime+ (" "*(15-len(newTime)))+"`"+invite.channel.mention +"\n"
    embed = discord.Embed(color=0x00FF00, description=inviteText)
    embed.set_author(name=ctx.author.display_name+"#"+str(ctx.author.discriminator)+"'s Invites", icon_url=ctx.author.display_avatar.url)
    await ctx.respond(embed=embed)
  else:
    await error(ctx, "You have no active invites")


@bot.slash_command(description="Display your servers invite leaderboard",guild_ids=guild_ids)
async def ileaderboard(ctx, page:Option(int, "Page on the leaderboard", required=False, default=None)):
  if db[str(ctx.guild.id)]["users"]:
    #get page
    if page == None:
      page = 1
    tmp = {}
    tmp = dict(db[str(ctx.guild.id)]["users"])
    #make new dictionary to sort
    tempdata = {}
    for key in tmp.keys():
      #check if it has any invitees or leaves
      if tmp[key][0] != 0 or tmp[key][1] != 0:
        tempdata[key] = tmp[key][0] - tmp[key][1]
    #sort data
    order = sorted(tempdata.items(), key=lambda x: x[1], reverse=True)
    #check length
    if int(page) >= 1 and int(page) <= math.ceil(len(order) / 10):
      #store all the users in inputText to later print
      inputText = ""
      count = 1
      for i in order:
        if count <= page * 10 and count >= page * 10 - 9:
          inputText += f"\n`[ {str(count)} ]` <@!{str(i[0])}> | ** {str(i[1])} ** invites (** {str(tmp[str(i[0])][2])} ** regular, **- {str(tmp[str(i[0])][3])} ** leaves)"
        count += 1
      #print embed
      embed = discord.Embed(color=0x00FF00, description=inputText)
      embed.set_author(name=ctx.guild.name+" Invite Leaderboard", icon_url=ctx.guild.icon.url)
      embed.set_footer(text="Page " + str(page) + "/" + str(math.ceil(len(order) / 10)))
      await ctx.respond(embed=embed)
    else:
      await error(ctx, "Invalid Page. Currently, this should be between `1` and `"+str(math.ceil(len(order) / 10))+"`.")
  else:
    await error(ctx, "Nobody has any invites in your server")


@bot.slash_command(description="Fetch your server's previous invites",guild_ids=guild_ids)
async def fetch(ctx):
  if staff(ctx):
    #reset inviters invites
    for invite in await ctx.guild.invites():
      #check if inviter in db
      if str(invite.inviter.id) in db[str(ctx.guild.id)]:
        #reset invites
        db[str(ctx.guild.id)]["users"][str(invite.inviter.id)][0] = 0
        db[str(ctx.guild.id)]["users"][str(invite.inviter.id)][1] = 0
    #loop through invites in guild
    for invite in await ctx.guild.invites():
      #check if inviter in db
      if str(invite.inviter.id) not in db[str(ctx.guild.id)]["users"]:
        db[str(ctx.guild.id)]["users"][str(invite.inviter.id)] = [0,0,"",0,0]
      #add to invites
      db[str(ctx.guild.id)]["users"][str(invite.inviter.id)][0] += int(invite.uses)
    embed = discord.Embed(color=0x00FF00, description="**Previous Invites Fetched**")
    await ctx.respond(embed=embed)
  else:
    await error(ctx, "You do not have the proper permissions to do this")


def editType(user, amount, type):
  if str(user.id) not in db[str(user.guild.id)]["users"]:
    db[str(user.guild.id)]["users"][str(user.id)] = [0,0,"",0,0]
  if type=="invites":
    db[str(user.guild.id)]["users"][str(user.id)][0] = amount
  elif type=="leaves":
    db[str(user.guild.id)]["users"][str(user.id)][1] = amount
  elif type=="bumps":
    db[str(user.guild.id)]["users"][str(user.id)][4] = amount

edit = SlashCommandGroup("edit", "Commands related to editing")

async def doEdit(ctx, set, user, type):
  if user == None:
    user = ctx.author
  if staff(ctx):
    editType(user, set, type)
    full = db[str(user.guild.id)]["users"][str(user.id)][0]
    leaves = db[str(user.guild.id)]["users"][str(user.id)][1]
    totalInvites = full - leaves
    if type != "bumps":
      addition = f"(**{full}** regular, **-{leaves}** leaves)"
    else:
      addition = ""
    embed = discord.Embed(color=0x00FF00,description=f"User now has **{totalInvites}** {type}! {addition}")
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    await ctx.respond(embed=embed)
  else:
    await error(ctx, "You do not have the proper permissions to do this")

@edit.command(description="Edit a user's invites", name="invites", guild_ids=guild_ids)
async def inv(ctx, set:Option(int, "The amount of invites to set to", required=True, default=None), user:Option(discord.Member,"The member to edit", required=False, default=None)):
  await doEdit(ctx, set, user, "invites")

@edit.command(description="Edit a user's leaves", guild_ids=guild_ids)
async def leaves(ctx, set:Option(int, "The amount of leaves to set to", required=True, default=None), user:Option(discord.Member,"The member to edit", required=False, default=None)):
  await doEdit(ctx, set, user, "leaves")

@edit.command(description="Edit a user's bumps", guild_ids=guild_ids)
async def bumps(ctx, set:Option(int, "The amount of bumps to set to", required=True, default=None), user:Option(discord.Member,"The member to edit", required=False, default=None)):
  await doEdit(ctx, set, user, "bumps")
  
    


@bot.event
async def on_ready():
  print(f"{bot.user.name} Online.")
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="minecraft"))
  #set online data
  global onlineTime
  onlineTime = datetime.now()
  #loop through guild and check them in db
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
        db[str(member.guild.id)]["users"][str(invite.inviter.id)] = [0,0,"",0,0]
      if str(member.id) not in db[str(member.guild.id)]["users"]:
        db[str(member.guild.id)]["users"][str(member.id)] = [0,0,"",0,0]
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

#add application commands
bot.add_application_command(edit)
  
keep_alive.keep_alive()  
bot.run(os.environ.get("TOKEN"))