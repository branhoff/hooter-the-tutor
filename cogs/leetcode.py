import discord
import requests
from discord.ext import commands


class LeetCodeCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='leetcode')
  async def leetcode(self, ctx, username: str):
    data = self.fetch_leetcode_profile(username)
    if data:
      embed = discord.Embed(title=f"LeetCode Profile: {username}",
                            color=discord.Color.blue())
      embed.add_field(name="Username", value=username, inline=False)
      embed.add_field(name="Easy Solved",
                      value=f"{data['easySolved']} / {data['totalEasy']}",
                      inline=True)
      embed.add_field(name="Medium Solved",
                      value=f"{data['mediumSolved']} / {data['totalMedium']}",
                      inline=True)
      embed.add_field(name="Hard Solved",
                      value=f"{data['hardSolved']} / {data['totalHard']}",
                      inline=True)
      await ctx.send(embed=embed)
    else:
      await ctx.send(f"Could not fetch data for {username}.")

  @staticmethod
  def fetch_leetcode_profile(username):
    url = f"https://leetcode-stats-api.herokuapp.com/{username}"
    response = requests.get(url)
    if response.status_code == 200:
      return response.json()
    else:
      return None
