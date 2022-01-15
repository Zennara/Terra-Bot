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
from discord.commands import permissions

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
  `/ileaderboard [page]` - View the servers invites leaderboard
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
  #button
  view = discord.ui.View()
  view.add_item(discord.ui.Button(emoji="<:zennara:931725235676397650>",label='Website', url='https://www.zennara.xyz', style=discord.ButtonStyle.url))
  #<:bot:929180626706374656>
  view.add_item(discord.ui.Button(emoji="<:bot:929180626706374656>",label='Discord', url='https://discord.gg/YHHvT5vWnV', style=discord.ButtonStyle.url))
  view.add_item(discord.ui.Button(emoji="💟",label='Donate', url='https://paypal.me/keaganlandfried', style=discord.ButtonStyle.url))
  #reply message
  await ctx.respond(embed=embed, view=view)


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
    await checkRewards(user)
  else:
    await error(ctx, "You do not have the proper permissions to do this")

TYPES = ["invites","leaves","bumps"]
async def getType(ctx: discord.AutocompleteContext):
  #Returns a list of colors that begin with the characters entered so far
  return [x for x in TYPES if x.startswith(ctx.value.lower())]

@bot.slash_command(description="Edit a user's invites, leaves, or bumps", guild_ids=guild_ids)
async def edit(ctx,type:Option(str, "Edit invites, leaves, or bumps", autocomplete=getType), set:Option(int, "The amount of invites to set to", required=True, default=None), user:Option(discord.Member,"The member to edit", required=False, default=None)):
  if type in TYPES:
    await doEdit(ctx, set, user, type)
  else:
    await error(ctx, "Invalid type to edit")


async def checkRewards(member):
  #check if in db
  if str(member.id) in  db[str(member.guild.id)]["users"]:
    #add to invites
    for irole in db[str(member.guild.id)]["iroles"]:
      roleIDs = []
      for role in member.roles:
        roleIDs.append(str(role.id))
      if db[str(member.guild.id)]["users"][str(member.id)][0] - db[str(member.guild.id)]["users"][str(member.id)][1] >= db[str(member.guild.id)]["iroles"][irole]:
        await member.guild.get_member(member.id).add_roles(member.guild.get_role(int(irole)),reason="Invite Reward",atomic=True)
      elif str(member.guild.get_role(int(irole)).id) in roleIDs:
        await member.guild.get_member(member.id).remove_roles(member.guild.get_role(int(irole)),reason="Invite Reward Removal",atomic=True)

@bot.slash_command(description="Add an invite role-reward", guild_ids=guild_ids)
async def addirole(ctx, role:Option(discord.Role, "The role to award", required=True, default=None), amount:Option(int, "The amount of invites the user must reach", required=True, default=None)):
  if amount > 0:
    if str(role.id) not in db[str(ctx.guild.id)]["iroles"]:
      db[str(ctx.guild.id)]["iroles"][str(role.id)] = amount
      embed = discord.Embed(color=0x00FF00, description=f"✅ Users will now get the role {role.mention} when reaching **{amount}** invites!")
      await ctx.respond(embed=embed)
      for member in ctx.guild.members:
        await checkRewards(member)
    else:
      await error(ctx, "Role already has an award assigned to it")
  else:
    await error(ctx, "Invite amount must be greater than `0`")

@bot.slash_command(description="Delete an invite role-reward", guild_ids=guild_ids)
async def delirole(ctx, role:Option(discord.Role, "The role the reward is assigned to", required=True, default=None), remove:Option(bool, "Whether to remove roles from users", required=False, default=None)):
  if str(role.id) in db[str(ctx.guild.id)]["iroles"]:
    del db[str(ctx.guild.id)]["iroles"][str(role.id)]
    embed = discord.Embed(color=0x00FF00, description=f"✅ {role.mention} no longer has a reward assigned to it")
    await ctx.respond(embed=embed)
    if remove == None:
      remove = False
    elif remove:
      if ctx.guild.get_role(role.id):
        if ctx.guild.get_member(bot.user.id).top_role > role:
          for member in ctx.guild.members:
            if role in member.roles:
              await member.remove_roles(ctx.guild.get_role(role.id))
        else:
          await error(ctx, f"Could not remove role {role.mention} : Missing Permissions")
  else:
    await error(ctx, "Role does not have an assigned reward")

@bot.slash_command(description="View all the server's invite role-rewards", guild_ids=guild_ids)
async def iroles(ctx):
  if db[str(ctx.guild.id)]["iroles"]:
    count = 0
    #get all RR messages
    embed = discord.Embed(color=0x00FF00, description="**Invite Role-Rewards**")
    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
    for irole in db[str(ctx.guild.id)]["iroles"]:
      if count == 25:
        count = 0
        await ctx.send(embed=embed)
        embed = discord.Embed(color=0x00FF00, description="")
      embed.add_field(name="Invites: "+str(db[str(ctx.guild.id)]["iroles"][irole]), value=f"**Role:** <@&{irole}>")
      count += 1
    await ctx.respond(embed=embed)
  else:
    await error(ctx, "The server does not have any invite role-rewards")

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
      print(f"{member.name} JOINED with {invite.code} from {invite.inviter}\n")
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
  #add to leaves
  #check if left member is in db
  if str(member.id) in db[str(member.guild.id)]["users"]:
    #ensure there was inviter
    if db[str(member.guild.id)]["users"][str(member.id)][2] != "":
      #check if inviter is in db
      if str(db[str(member.guild.id)]["users"][str(member.id)][3]) not in db[str(member.guild.id)]["users"]:
        db[str(member.guild.id)]["users"][str(db[str(member.guild.id)][str(member.id)][3])] = [0,0,"",0,0]
      #add to inviter leaves
      db[str(member.guild.id)]["users"][str(db[str(member.guild.id)]["users"][str(member.id)][3])][1] += 1
      print(f"{member.name} LEFT with {invite.code} from {invite.inviter}")
      await checkRewards(member.guild.get_member(int(db[str(member.guild.id)]["users"][str(member.id)][3])))
  #write cache
  invs[member.guild.id] = await member.guild.invites()

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
  
keep_alive.keep_alive()  
bot.run(os.environ.get("TOKEN"))