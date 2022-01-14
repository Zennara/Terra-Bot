import discord
import os
import keep_alive
from replit import db
import requests

bot = discord.Bot()

guild_ids = [806706495466766366]

#api limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

@bot.event
async def on_ready():
    print(f"{bot.user.name} Online.")

@bot.slash_command(guild_ids=guild_ids)
async def hello(ctx, opt):
    await ctx.respond("Hello!")

  
keep_alive.keep_alive()  
bot.run(os.environ.get("TOKEN"))