import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed, ui
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

class RSVPView(ui.View):
    def __init__(self, creator, title, time, location, details):
        super().__init__(timeout=None)
        self.creator = creator
        self.title = title
        self.time = time
        self.location = location
        self.details = details
        self.going = set()
        self.not_going = set()
        self.message = None

    def format_embed(self):
        embed = Embed(title=f"📅 {self.title}", description="Click a button to RSVP!", color=discord.Color.gold())
        embed.add_field(name="🕒 Time", value=self.time, inline=False)
        embed.add_field(name="📍 Location", value=self.location, inline=False)
        embed.add_field(name="📝 Details", value=self.details or "None", inline=False)
        embed.add_field(name="✅ Going", value="\n".join(u.mention for u in self.going) or "No one yet", inline=True)
        embed.add_field(name="❌ Not Going", value="\n".join(u.mention for u in self.not_going) or "No one yet", inline=True)
        embed.set_footer(text=f"Event created by {self.creator.display_name}")
        embed.timestamp = datetime.now(pytz.timezone("US/Eastern"))
        return embed

    @ui.button(label="✅ Going", style=discord.ButtonStyle.success)
    async def yes(self, interaction: Interaction, button: ui.Button):
        self.not_going.discard(interaction.user)
        self.going.add(interaction.user)
        await self.update(interaction)

    @ui.button(label="❌ Not Going", style=discord.ButtonStyle.danger)
    async def no(self, interaction: Interaction, button: ui.Button):
        self.going.discard(interaction.user)
        self.not_going.add(interaction.user)
        await self.update(interaction)

    async def update(self, interaction: Interaction):
        await interaction.response.edit_message(embed=self.format_embed(), view=self)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="event", description="Create an interactive RSVP event.")
    @app_commands.describe(
        title="Event title",
        time="When is the event?",
        location="Where is it?",
        details="More information about the event"
    )
    async def event(self, interaction: Interaction, title: str, time: str, location: str, details: str = ""):
        await interaction.response.defer()

        debug_command(
            "event", interaction.user,
            title=title,
            time=time,
            location=location,
            details=details
        )

        view = RSVPView(
            creator=interaction.user,
            title=title,
            time=time,
            location=location,
            details=details
        )

        embed = view.format_embed()
        msg = await interaction.followup.send(embed=embed, view=view, wait=True)
        view.message = msg

# --- Cog Setup ---
async def setup(bot):
    await bot.add_cog(Events(bot))

