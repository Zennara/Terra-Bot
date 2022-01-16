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
bot = discord.Bot(intents=intents)

guild_ids = [761036747504484392, 806706495466766366]

invs = {}

onlineTime = datetime.now()

#api limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")


"""
<----------------------------------FUNCTIONS----------------------------------->
"""
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
  db[str(guild.id)] = {"mod":0, "iroles":{}, "roles":[], "star":[False,"⭐",0,[],0], "users":{}}
  #guild - [iroles, users]
  #users format - [invites,leaves,code,inviter,bumps]

def checkGuild(guild):
  if guild != None:
    if str(guild.id) not in db:
      resetDB(guild)

async def error(ctx, code):
  embed = discord.Embed(color=0xFF0000, description= f"❌ {code}")
  await ctx.respond(embed=embed, ephemeral=True)

async def confirm(ctx, code, eph): 
  embed = discord.Embed(color=0x00FF00, description= f"✅ {code}")
  await ctx.respond(embed=embed, ephemeral=eph)

def staff(ctx):
  checkGuild(ctx.guild)
  mod = db[str(ctx.guild.id)]["mod"]
  if hasattr(ctx, "author"):
    if ctx.author == ctx.guild.owner:
        return True
    if mod != 0:
      if ctx.guild.get_role(mod) <= ctx.author.top_role:
        return True
  else:
    if ctx.user.id == ctx.guild.owner.id:
      return True
    if mod != 0:
      if ctx.guild.get_role(mod) <= ctx.guild.get_member(ctx.user.id).top_role:
        return True
  return False



"""
<----------------------------------GENERAL MANAGEMENT----------------------------------->
"""
class helpClass(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)

    bwebsite = discord.ui.Button(label='Website', style=discord.ButtonStyle.gray, url='https://www.zennara.me', emoji="<:zennara:931725235676397650>")
    self.add_item(bwebsite)
    bdiscord = discord.ui.Button(label='Discord', style=discord.ButtonStyle.gray, url='https://www.discord.gg/YHHvT5vWnV', emoji="<:bot:929180626706374656>")
    self.add_item(bdiscord)
    bdonate = discord.ui.Button(label='Donate', style=discord.ButtonStyle.gray, url='https://www.paypal.me/keaganlandfried', emoji="💟")
    self.add_item(bdonate)

  @discord.ui.select(custom_id="select-2", placeholder='View help with a specific section of commands', min_values=1, max_values=1, options=[
    discord.SelectOption(label='General', value="General", description='View this for general ands server commands', emoji="❓"),
    discord.SelectOption(label='Invite Tracker', value="Invite Tracker", description='Track invites and award roles based off them', emoji='✉️'),
    discord.SelectOption(label='Award Roles', value="Award Roles", description='Award roles on dropdown menus and reactions', emoji='🖱️'),
    discord.SelectOption(label='Starboard', value="Starboard", description='Highlight messages that reach x amount of emojis', emoji='⭐'),  
    discord.SelectOption(label='Polls', value="Polls", description='Easily configurable polls for voting!', emoji='📊')
  ])
  async def select_callback(self, select, interaction):
    role = interaction.guild.roles[random.randint(1, len(interaction.guild.roles)-1)]
    if select.values[0] == "General":
      text = """
      This bot uses **slash commands**. This mean all bot commands starts with `/`.
      You can find more help in my [Discord server](https://discord.gg/YHHvT5vWnV).
    
      **Commands**
      `/help` - Show the preview help page
      `/ping` - Ping the bot for it's uptime
      """
      if staff(interaction):
        text += """
        **Mod Commands**
        `/clear` - Clears the guilds database
        """
    elif select.values[0] == "Invite Tracker":
      text = f"""
      The **Invite Tracker** module can be used for keeping track of your user's invites and awarding them roles if they reach a specific amount! For example, if set, users could get the role {role.mention} after inviting {random.randint(5, 15)} people! This is, of course, assuming they stay in the server as leaves are also tracked.
    
      **Commands**
      `/invites [user]` - Check the invites of a user or yourself
      `/ileaderboard [page]` - View the servers invites leaderboard
      `/invite` - View all your active invites
      `/iroles` - Display the server's invite role rewards
      """
      if staff(interaction):
        text += """
        **Mod Commands**
        `/fetch` - Fetch the servers previous invites
        `/edit <invites|leaves> <amount> [member]` - Edit the invites or leaves of a user
        `/addirole <invites> <role>` - Add an invite role reward
        `/delirole <role>` - Delete an invite role reward
        """
    elif select.values[0] == "Award Roles":
      text = """
      The **Award Roles** module is perfect for assigning members roles either after they react to a message, or selecting their roles from a modern dropdown menu.
    
      **Commands**
      `/showrr` - List the server's role reaction rewards
      """
      if staff(interaction):
        text += """
        **Mod Commands**
        `/drophere` - Place the dropdown for roles in the current channel
        `/addrr <message> <role> <emoji>` - Add a role reaction reward
        `/delrr <message> <role> <emoji>` - Delete a role reaction reward
        """
    elif select.values[0] == "Starboard":
      text = """
      The **Starboard** module is a  relatively simple module. Have you ever wanted to have a type of **hall of fame** showcase channel? Well, with this module you do exactly so. Messages that recieve `x` amount of emojis (custom or unicode!) can be placed forever in a pre-determined channel in the form of a **webhook**. This name, profile picure, attachments, media, and embeds will be carries over to the starboard channel. Mods can also select channels to *ignore* from this feature.
    
      **Commands**
      `/showrr` - List the server's role reaction rewards
      """
      if staff(interaction):
        text += """
        **Mod Commands**
        `/drophere` - Place the dropdown for roles in the current channel
        `/addrr <message> <role> <emoji>` - Add a role reaction reward
        `/delrr <message> <role> <emoji>` - Delete a role reaction reward
        """
    elif select.values[0] == "Polls":
      text = """
      The **Polls** module can be used to cast votes on different things in your server. Polls are designed to be easy to set up in a matter of seconds.
      
      **Commands**
      `/poll simple` - Create a simple, two option poll
      `/poll multi` - Create a poll with up to 10 options
      """
      if staff(interaction):
        text += """
        """
      
    embed = discord.Embed(color=0x00FF00,description=text, title=select.values[0])
    embed.set_footer(text="________________________\n<> Required | [] Optional\nMade By Zennara#8377")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
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
  #reply message
  await ctx.respond(embed=embed, view=helpClass())


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
    await confirm(ctx, "Guild database cleared", True)
  else:
    await error(ctx, "You do not have the proper permissions to do this")

@bot.slash_command(description="Reset the database",guild_ids=guild_ids, default_permissions=False)
@permissions.is_user(427968672980533269)
async def reset(ctx):
  for guild in bot.guilds:
    resetDB(guild)
  await confirm(ctx, "Database was reset", True)


"""
<----------------------------------INVITE MANAGEMENT----------------------------------->
"""
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
    await confirm(ctx, "**Previous Invites Fetched**", True)
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
@bot.slash_command(description="Edit a user's invites, leaves, or bumps", guild_ids=guild_ids)
async def edit(ctx,type:Option(str, "Edit invites, leaves, or bumps", choices=TYPES), set:Option(int, "The amount of invites to set to", required=True, default=None), user:Option(discord.Member,"The member to edit", required=False, default=None)):
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
      await confirm(ctx, f"Users will now get the role {role.mention} when reaching **{amount}** invites!", False)
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
    await confirm(ctx, f"{role.mention} no longer has a reward assigned to it", False)
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


"""
<----------------------------------REACTION AND DROPDOWN ROLE REWARDS----------------------------------->
"""
class react(discord.ui.View):
  def __init__(self):
      super().__init__(timeout=None)

  ROLE_IDS = [923728545224732712, 931784471039049769, 931784416483770408]
  @discord.ui.select(custom_id="select-1", placeholder='Pick your colour', min_values=0, max_values=3, options=[
    discord.SelectOption(label='Test1', value=ROLE_IDS[0], description='This is for test1', emoji='🟥'),
    discord.SelectOption(label='Test2', value=ROLE_IDS[1], description='This is for test2', emoji='🟩'),
    discord.SelectOption(label='Test3', value=ROLE_IDS[2], description='This is for test3', emoji='🟦')
  ])
  async def select_callback(self, select, interaction):
    text = ""
    global ROLE_IDS
    for opt in select.values:
      text = f"{text}{interaction.guild.get_role(int(opt)).mention}, "
    await interaction.response.send_message(f'You will now be notified for {text}'[:-2], ephemeral=True)

@bot.slash_command(description="Place the drop-down role reward menu in this channel", guild_ids=guild_ids)
async def drophere(ctx):
  embed = discord.Embed(color=0x00FF00, description="**Select the roles you wish to access.**")
  await ctx.send(embed=embed, view=react())
  await confirm(ctx, f"Dropdown menu sent", True)

@bot.slash_command(description="Add a role reaction reward", guild_ids=guild_ids)
async def addrr(ctx, message:Option(str, "The message link to add the reaction to", required=True), emoji:Option(str, "The emoji for the reaction", required=True), role:Option(discord.Role, "The role to reward", required=True)):
  channelID = message[-37:-19]
  messageID = message[-18:]
  if channelID.isnumeric() and messageID.isnumeric():
    channelID = int(channelID)
    messageID = int(messageID)
    if bot.get_channel(int(channelID)):
      channel = bot.get_channel(int(channelID))
      if await channel.fetch_message(int(messageID)):
        msg = await channel.fetch_message(int(messageID))
        if role <= ctx.guild.get_member(bot.user.id).top_role:
          try:
            await msg.add_reaction(emoji)
          except:
            await error(ctx, "Invalid emoji")
          else:
            if [channelID,messageID,role.id,emoji] not in db[str(ctx.guild.id)]["roles"]:
              checkGuild(ctx.guild)
              db[str(ctx.guild.id)]["roles"].append([channelID,messageID,role.id,emoji])
              await confirm(ctx, f"{emoji} {role.mention} reaction reward added [here]({msg.jump_url})", True)
            else:
              await error(ctx, "Exact role reaction reward already exists")
        else:
          await error(ctx, "Missing Permissions: Can not award this role")
      else:
        await error(ctx, "Invalid Message")
    else:
      await error(ctx, "Channel ID is invalid")
  else:
    await error(ctx, "Invalid message link")

@bot.slash_command(description="Delete a role reaction reward", guild_ids=guild_ids)
async def delrr(ctx, message:Option(str, "The message link of the reaction reward", required=True), emoji:Option(str, "The emoji from the reaction", required=True), role:Option(discord.Role, "The role to remove", required=True)):
  channelID = message[-37:-19]
  messageID = message[-18:]
  if channelID.isnumeric() and messageID.isnumeric():
    channelID = int(channelID)
    messageID = int(messageID)
    if bot.get_channel(int(channelID)):
      channel = bot.get_channel(int(channelID))
      if await channel.fetch_message(int(messageID)):
        msg = await channel.fetch_message(int(messageID))
        try:
          await msg.add_reaction(emoji)
        except:
          await error(ctx, "Invalid emoji")
        else:
          if [channelID,messageID,role.id,emoji] in db[str(ctx.guild.id)]["roles"]:
            checkGuild(ctx.guild)
            db[str(ctx.guild.id)]["roles"].remove([channelID,messageID,role.id,emoji])
            await msg.remove_reaction(emoji, ctx.guild.get_member(bot.user.id))
            await confirm(ctx, f"{emoji} {role.mention} reaction reward removed from [here]({msg.jump_url})", True)
          else:
            await error(ctx, "Role reaction reward does not exist")
      else:
        await error(ctx, "Invalid Message")
    else:
      await error(ctx, "Channel ID is invalid")
  else:
    await error(ctx, "Invalid message link")

@bot.slash_command(description="List the server's role reactions", guild_ids=guild_ids)
async def showrr(ctx):
  if db[str(ctx.guild.id)]["roles"]:
    text = ""
    for role in db[str(ctx.guild.id)]["roles"]:
      channel = bot.get_channel(int(role[0]))
      m = await channel.fetch_message(int(role[1]))
      text += f"[Message Jump]({m.jump_url}) | {ctx.guild.get_role(int(role[2])).mention} | {role[3]}\n"
    embed = discord.Embed(description=text, color=0x00FF00)
    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
    await ctx.respond(embed=embed)
  else:
    await error(ctx, "No reaction role rewards on this server")


"""
<----------------------------------STARBOARD COMMANDS----------------------------------->
"""
star = SlashCommandGroup("star", "Starboard commands", guild_ids=guild_ids)

@star.command(description="Toggle the starboard feature", guild_ids=guild_ids)
async def toggle(ctx, flag:Option(bool, "Whether to enable or disable this module", required=True)):
  checkGuild(ctx.guild)
  db[str(ctx.guild.id)]["star"][0] =  flag
  await confirm(ctx, f"The starboard module was set to **{flag}**", True)

@star.command(description="Set the starboard emoji", guild_ids=guild_ids)
async def emoji(ctx, emoji:Option(str, "Set the starboard emoji. Leave blank to view the current emoji", required=False, default=None)):
  checkGuild(ctx.guild)
  if emoji == None:
    current = db[str(ctx.guild.id)]["star"][1]
    try:
      async for message in ctx.channel.history(limit=1):
        await message.remove_reaction(current, ctx.guild.get_member(bot.user.id))
        break
    except:
      await error(ctx, "This emoji is no longer valid. The starboard emoji was set to ⭐")
    else:
      emoji = db[str(ctx.guild.id)]["star"][1]
      await confirm(ctx, f"The current starbord emoji is  {emoji}", False)
  else:
    try:
      async for message in ctx.channel.history(limit=1):
        await message.remove_reaction(emoji, ctx.guild.get_member(bot.user.id))
        break
    except:
      await error(ctx, "This is not a valid emoji or bot does not have access")
    else:
      db[str(ctx.guild.id)]["star"][1] = emoji
      await confirm(ctx, f"The emoji for starboard was set to  {emoji}", False)

@star.command(name="channel", description="Set the starboard send channel", guild_ids=guild_ids)
async def cnl(ctx, set:Option(discord.TextChannel, "Set the starboard channel. Leave blank to view the starboard channel", required=False, default=None)):
  checkGuild(ctx.guild)
  if set == None:
    if db[str(ctx.guild.id)]["star"][0] == False:
      await error(ctx, "Starboard is currently disabled")
    else:
      flag = db[str(ctx.guild.id)]["star"][2]
      if flag != 0:
        if ctx.guild.get_channel(int(flag)) != None:
          await confirm(ctx, f"The current starboard channel is {ctx.guild.get_channel(int(flag)).mention}", False)
        else:
          db[str(ctx.guild.id)]["star"][2] = 0
          await error(ctx, "This channel no longer exists. Channel reset to default `None`")
      else:
        await error(ctx, "There is no current Starboard channel")
  else:
    text=""
    if db[str(ctx.guild.id)]["star"][0] == False:
      text = "Starboard was auto-enabled\n"
      db[str(ctx.guild.id)]["star"][0] = True
    db[str(ctx.guild.id)]["star"][2] = set.id
    await confirm(ctx, f"{text}The starboard channel is now set to {set.mention}", True)

@star.command(description="Add, remove, or view ignored channels", guild_ids=guild_ids)
async def ignore(ctx, ign:Option(bool, "Leave this blank to view ignored channels", required=False, defualt=None)):
  checkGuild(ctx.guild)
  if ign == True:
    db[str(ctx.guild.id)]["star"][3].append(ctx.channel.id)
    await confirm(ctx, "This channel will **now** be ignored from starboard", True)
  elif ign == False:
    if ctx.channel.id in db[str(ctx.guild.id)]["star"][3]:
      db[str(ctx.guild.id)]["star"][3].remove(ctx.channel.id)
      await confirm(ctx, "This channel will **no longer** be ignored from starboard", True)
    else:
      await error(ctx, "This channel is not currently ignored")
  else:
    if db[str(ctx.guild.id)]["star"][3]:
      text = ""
      for ignored in db[str(ctx.guild.id)]["star"][3]:
        if ctx.guild.get_channel(ignored) != None:
          text = f"{text}{ctx.guild.get_channel(ignored).mention}\n"
      embed = discord.Embed(title="⭐ Ignored Channels", description=text, color=0x00FF00)
      await ctx.respond(embed=embed)
    else:
      await error(ctx, "There are no ignored channels for starboard")

@star.command(description="Set the amount of reactions for starboard", guild_ids=guild_ids)
async def amount(ctx, amount:Option(int, "The amount of reactions required for starboard", required=True)):
  checkGuild(ctx.guild)
  if amount > 0:
    db[str(ctx.guild.id)]["star"][4] = amount
    await confirm(ctx, f"The amount of reactions for starboard is now **{amount}**", False)
  else:
    await error(ctx, "This value must be greater than `0`")

bot.add_application_command(star)


"""
<----------------------------------POLLS COMMANDS----------------------------------->
"""
poll = SlashCommandGroup("poll", "Polling commands", guild_ids=guild_ids)

@poll.command(description="Create a simple poll", guild_ids=guild_ids)
async def simple(ctx, description:Option(str, "The description of the poll")):
  #split current datetime
  nowDT = str(datetime.now()).split()
  nowDate = nowDT[0]
  nowTime = str(datetime.strptime(str(nowDT[1][0 : len(nowDT[1]) - 7]), "%H:%M:%S").strftime("%I:%M %p"))
  embed = discord.Embed(color=0x00FF00, description=f"**📊 | {description}**")
  embed.set_footer(text=nowDate + " at " + nowTime)
  inter = await ctx.send(embed=embed)
  await inter.add_reaction("👍")
  await inter.add_reaction("👎")
  await confirm(ctx, "Simple poll created!", True)

@poll.command(description="Create a multi-option poll", guild_ids=guild_ids)
async def multi(ctx, description:Option(str, "The first option of the poll"), option_1:Option(str, "The first option of the poll", required=True), option_2:Option(str, "The second option of the poll", required=True), option_3:Option(str, "The third option of the poll", required=True), option_4:Option(str, "The fourth option of the poll", required=False), option_5:Option(str, "The fifth option of the poll", required=False), option_6:Option(str, "The sixth option of the poll", required=False), option_7:Option(str, "The seventh option of the poll", required=False), option_8:Option(str, "The eigth option of the poll", required=False), option_9:Option(str, "The ninth option of the poll", required=False), option_10:Option(str, "The tenth option of the poll", required=False)):
  #numbers
  nums = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "0️⃣"]
  #split current datetime
  nowDT = str(datetime.now()).split()
  nowDate = nowDT[0]
  nowTime = str(datetime.strptime(str(nowDT[1][0 : len(nowDT[1]) - 7]), "%H:%M:%S").strftime("%I:%M %p"))
  options = [option_1,option_2,option_3,option_4,option_5,option_6,option_7,option_8,option_9,option_10]
  opts = ""
  count = 0
  for item in options:
    if item != None:
      opts = f"{opts}\n{nums[count]} | {item}"
      count += 1
  embed = discord.Embed(color=0x00FF00, description=f"**📊 | {description}**\n{opts}")
  embed.set_footer(text=nowDate + " at " + nowTime)
  inter = await ctx.send(embed=embed)
  for x in range(0,count):
    await inter.add_reaction(nums[x])
  await confirm(ctx, "Multi-option poll created!", True)

bot.add_application_command(poll)   
"""
<----------------------------------CONTEXT MENU COMMANDS----------------------------------->
"""
@bot.message_command(name="Get Message ID", guild_ids=guild_ids)
async def messageid(ctx, message: discord.Message):
  await confirm(ctx, f"Message ID: `{message.id}`", True)

@bot.message_command(name="Get Channel ID", guild_ids=guild_ids)
async def channelid(ctx, message: discord.Message):
  await confirm(ctx, f"{message.channel.mention} ID: `{message.channel.id}`", True)

@bot.message_command(name="Get Guild ID", guild_ids=guild_ids)
async def guildid(ctx, message: discord.Message):
  await confirm(ctx, f"{message.guild.name} ID: `{message.guild.id}`", True)

@bot.user_command(name="Get User ID", guild_ids=guild_ids)
async def mention(ctx, member: discord.Member):
  await confirm(ctx, f"{member.name} ID: `{member.id}`", True)

"""
<----------------------------------EVENTS----------------------------------->
"""
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

  #persistance
  bot.add_view(react())
  bot.add_view(helpClass())

@bot.event
async def on_raw_reaction_add(payload):
  #<--------REACTION REWARDS--------->
  if payload.member.id != bot.user.id:
    for role in payload.member.guild.roles:
      if [payload.channel_id,payload.message_id,role.id,str(payload.emoji)] in db[str(payload.guild_id)]["roles"]:
        await payload.member.add_roles(payload.member.guild.get_role(int(role.id)), atomic=True)

  #<------------STARBOARD------------->
  #check if enabled
  guild = bot.get_guild(payload.guild_id)
  if db[str(guild.id)]["star"][0]:
    #check not restricted category
    channel = guild.get_channel(payload.channel_id)
    starchannel = guild.get_channel(db[str(guild.id)]["star"][2])
    noStarboard = db[str(guild.id)]["star"][3]
    ej = db[str(guild.id)]["star"][1]
    amount = db[str(guild.id)]["star"][4]
    if str(channel.category.id) not in noStarboard and str(channel.id) not in noStarboard:
      #check for star
      if payload.emoji.name == ej:
        message = await channel.fetch_message(payload.message_id)
        count = {react.emoji: react.count for react in message.reactions}
        #check star count
        if count[ej] >= amount:
          #check msg already in starchannel
          messages = await starchannel.history(limit=1000).flatten()
          done = False
          for msg in messages:
            if msg.content.startswith(message.jump_url):
              done = True
          if not done:
            embed = discord.Embed(color=0xFFD700, description= message.content)
            embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.display_avatar.url)
            #get all files
            files = []
            for ach in message.attachments:
              files.append(await ach.to_file())
            #get all non-link embeds
            doEmbeds = True
            for emb in message.embeds:
              if str(emb.provider) != "EmbedProxy()":
                doEmbeds = False
            #define webhook
            #get webhook
            hooks = await starchannel.webhooks()
            hookFind = False
            if hooks:
              x=0
              for hook in hooks:
                if hook.token != None:
                  webhook = hooks[x]
                  hookFind = True
                  break
                x += 1
            if not hookFind:
              webhook= await starchannel.create_webhook(name="TerraBot Required",avatar=None,reason="For starboard")
            await webhook.send(username=message.author.display_name, avatar_url=message.author.display_avatar.url, content=message.jump_url+"\n\n"+message.content, files=files)
            #if all non-link embeds
            if doEmbeds:
              await webhook.send(username=message.author.display_name, avatar_url=message.author.display_avatar.url, embeds=message.embeds)
  

@bot.event
async def on_raw_reaction_remove(payload):
  #<--------REACTION REWARDS--------->
  if payload.user_id != bot.user.id:
    for role in bot.get_guild(int(payload.guild_id)).roles:
      if [payload.channel_id,payload.message_id,role.id,str(payload.emoji)] in db[str(payload.guild_id)]["roles"]:
        await bot.get_guild(int(payload.guild_id)).get_member(int(payload.user_id)).remove_roles(bot.get_guild(int(payload.guild_id)).get_role(int(role.id)), atomic=True)

def checkRR(check, guild):
  checkGuild(guild)
  itemsToRemove = []
  #loop through roles
  for item in db[str(guild.id)]["roles"]:
    #check if channel that was deleted in db
    if check in item:
      #add to deletion
      itemsToRemove.append(item)
  #delete
  for item in itemsToRemove:
    db[str(guild.id)]["roles"].remove(item)

@bot.event
async def on_guild_role_delete(role):
  checkRR(role.id, role.guild)

@bot.event
async def on_guild_channel_delete(channel):
  checkRR(channel.id, channel.guild)

@bot.event
async def on_guild_emojis_update(guild, before, after):
  s = set(after)
  diff = [x for x in before if x not in s]
  checkRR(str(diff[0]), guild)

@bot.event
async def on_raw_message_delete(payload):
  checkRR(payload.message_id, bot.get_guild(payload.guild_id))

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