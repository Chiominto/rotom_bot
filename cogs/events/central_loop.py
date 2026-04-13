import asyncio

from discord.ext import commands

# 🧹 Import your scheduled tasks
from utils.logs.pretty_log import pretty_log
from utils.background_task.central_loop_task.berry_checker import berry_reminder_checker
from utils.background_task.central_loop_task.berry_water_checker import (
    berry_water_reminder,
)

# 🍰──────────────────────────────
#   🎀 Cog: CentralLoop
#   Handles background tasks every 60 seconds
# 🍰──────────────────────────────
class CentralLoop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop_task = None

    def cog_unload(self):
        if self.loop_task and not self.loop_task.done():
            self.loop_task.cancel()
            pretty_log(
                "warn",
                "Loop task cancelled on cog unload.",
                label="CENTRAL LOOP",
                bot=self.bot,
            )

    async def central_loop(self):
        """Background loop that ticks every 60 seconds"""
        await self.bot.wait_until_ready()


        pretty_log(
            "",
            "✅ Central loop started!",
            label="🧭 CENTRAL LOOP",
            bot=self.bot,
        )
        while not self.bot.is_closed():
            try:
                """pretty_log(
                    "",
                    "🔂 Running background checks...",
                    label="🧭 CENTRAL LOOP",
                    bot=self.bot,
                )"""

                # Check berry water reminders
                await berry_water_reminder(bot=self.bot)

                # Check berry growth reminders
                await berry_reminder_checker(bot=self.bot)

            except Exception as e:
                pretty_log(
                    "error",
                    f"{e}",
                    label="CENTRAL LOOP ERROR",
                    bot=self.bot,
                )
            await asyncio.sleep(60)  # ⏱ tick interval

    @commands.Cog.listener()
    async def on_ready(self):
        """Start the loop automatically once the bot is ready"""
        if not self.loop_task:
            self.loop_task = asyncio.create_task(self.central_loop())


# ====================
# 🔹 Setup
# ====================
async def setup(bot: commands.Bot):
    cog = CentralLoop(bot)
    await bot.add_cog(cog)

    print("\n[📋 CENTRAL LOOP CHECKLIST] Scheduled tasks loaded:")
    print("  ─────────────────────────────────────────────")
    print("  ✅ ⏰  berry_reminder_checker")
    print("  ✅ ⏰  berry_water_reminder")
    print("  🧭 CentralLoop ticking every 60 seconds!")
    print("  ─────────────────────────────────────────────\n")
