import logging
from discord.ext import commands
from discord import Member
from cogs.streaks import load_streaks
from responses import get_hooter_explanation


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reintroduce")
    async def reintroduce(self, ctx, member: Member = None):
        """Command to reintroduce the system. If a member is mentioned, it addresses them specifically."""
        if member:
            message = f"Hey {member.display_name}, let me reintroduce you to how we keep things engaging around here!"
        else:
            message = "Looks like someone needs a refresher on how our awesome system works!"

        explanation = get_hooter_explanation()
        await ctx.send(f"{message}\n{explanation}")

    @commands.command(name="streak")
    async def streak(self, ctx, member: Member = None) -> None:
        if member is None:
            member = ctx.author

        streaks_data = load_streaks()
        await self.display_streak(ctx, member, streaks_data)

    async def display_streak(self, ctx, member, streaks_data):
        user_id = str(member.id)

        if user_id in streaks_data:
            current_streak = streaks_data[user_id]["current_streak"]
            longest_streak = streaks_data[user_id]["longest_streak"]
            username = streaks_data[user_id]["username"]
            message = f"{username}'s streaks:\n" \
                      f"Current streak: {current_streak} days\n" \
                      f"Longest streak: {longest_streak} days"
            await ctx.send(message)
        else:
            await ctx.send(f"{member.mention} hasn't started a streak yet.")

