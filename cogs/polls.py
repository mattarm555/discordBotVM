import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import asyncio
from datetime import datetime
import pytz

# --- Color Codes ---
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def debug_command(name, user, **kwargs):
    print(f"{GREEN}[COMMAND] /{name}{RESET} triggered by {YELLOW}{user.display_name}{RESET}")
    if kwargs:
        print(f"{CYAN}Input:{RESET}")
        for key, value in kwargs.items():
            print(f"  {key}: {value}")

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create a custom emoji poll with 2–6 options and a closing timer.")
    @app_commands.describe(
        question="Your poll question",
        duration_minutes="How many minutes until the poll closes?",
        anonymous="Hide voter usernames in the final results?",
        option1_text="Option 1 text", option1_emoji="Option 1 emoji",
        option2_text="Option 2 text", option2_emoji="Option 2 emoji",
        option3_text="Option 3 text", option3_emoji="Option 3 emoji",
        option4_text="Option 4 text", option4_emoji="Option 4 emoji",
        option5_text="Option 5 text", option5_emoji="Option 5 emoji",
        option6_text="Option 6 text", option6_emoji="Option 6 emoji"
    )
    async def poll(
        self,
        interaction: Interaction,
        question: str,
        duration_minutes: int,
        anonymous: bool,
        option1_text: str, option1_emoji: str,
        option2_text: str, option2_emoji: str,
        option3_text: str = None, option3_emoji: str = None,
        option4_text: str = None, option4_emoji: str = None,
        option5_text: str = None, option5_emoji: str = None,
        option6_text: str = None, option6_emoji: str = None
    ):
        await interaction.response.defer()

        # Debug
        debug_command(
            "poll", interaction.user,
            question=question,
            duration=f"{duration_minutes} min",
            anonymous=anonymous,
            options={f"{text}": emoji for text, emoji in [
                (option1_text, option1_emoji),
                (option2_text, option2_emoji),
                (option3_text, option3_emoji),
                (option4_text, option4_emoji),
                (option5_text, option5_emoji),
                (option6_text, option6_emoji)
            ] if text and emoji}
        )

        # Build valid options list
        options = []
        for text, emoji in [
            (option1_text, option1_emoji),
            (option2_text, option2_emoji),
            (option3_text, option3_emoji),
            (option4_text, option4_emoji),
            (option5_text, option5_emoji),
            (option6_text, option6_emoji)
        ]:
            if text and emoji:
                options.append((text, emoji))

        if len(options) < 2:
            await interaction.followup.send(embed=Embed(title="❌ Error", description="You need at least 2 options.", color=discord.Color.red()), ephemeral=True)
            return

        # Send poll embed
        embed = Embed(title="📊 Poll", description=question, color=discord.Color.blurple())
        for text, emoji in options:
            embed.add_field(name=f"{emoji} {text}", value=" ", inline=False)
        embed.set_footer(text=f"Poll closes in {duration_minutes} minutes • Created by {interaction.user.display_name}")
        embed.timestamp = datetime.now(pytz.timezone("US/Eastern"))

        msg = await interaction.followup.send(embed=embed, wait=True)

        for _, emoji in options:
            try:
                await msg.add_reaction(emoji)
            except:
                pass  # Skip invalid emojis

        # Wait for poll to finish
        await asyncio.sleep(duration_minutes * 60)

        # Fetch updated message
        msg = await interaction.channel.fetch_message(msg.id)

        # Tally votes
        votes = {}
        user_voted = set()

        for reaction in msg.reactions:
            if str(reaction.emoji) not in [e for _, e in options]:
                continue
            async for user in reaction.users():
                if user.bot:
                    continue
                if user.id not in user_voted:
                    votes.setdefault(str(reaction.emoji), []).append(user)
                    user_voted.add(user.id)

        # Build results
        result_embed = Embed(title="📊 Poll Closed", description=question, color=discord.Color.gray())
        for text, emoji in options:
            voters = votes.get(emoji, [])
            count = len(voters)
            value = f"**{count} vote(s)**" if anonymous else f"**{count} vote(s)**\n" + ", ".join(u.display_name for u in voters) or "No votes"
            result_embed.add_field(name=f"{emoji} {text}", value=value, inline=False)

        result_embed.set_footer(text=f"Poll created by {interaction.user.display_name}")
        await msg.edit(embed=result_embed)

# --- Cog setup ---
async def setup(bot):
    await bot.add_cog(Polls(bot))

