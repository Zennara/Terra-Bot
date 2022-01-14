import discord
import os

bot = discord.Bot()

guild_ids = [806706495466766366]

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=guild_ids)
async def hello(ctx):
    await ctx.respond("Hello!")
  
bot.run(os.environ.get("TOKEN"))