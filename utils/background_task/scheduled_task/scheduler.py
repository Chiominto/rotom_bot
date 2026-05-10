import zoneinfo
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.background_task.scheduled_task.daily_ball_reset import daily_ball_reset

from .goal_track_reset import monthly_goal_track_reset, weekly_goal_track_reset
from utils.background_task.scheduled_task.sched_helper import SchedulerManager
from utils.logs.pretty_log import pretty_log

NYC = zoneinfo.ZoneInfo("America/New_York")  # auto-handles EST/EDT

# 🛠️ Create a SchedulerManager instance with Asia/Manila timezone
scheduler_manager = SchedulerManager(timezone_str="Asia/Manila")


def format_next_run_manila(next_run_time):
    """
    Converts a timezone-aware datetime to Asia/Manila time and returns a readable string.
    """
    if next_run_time is None:
        return "No scheduled run time."
    # Convert to Manila timezone
    manila_tz = ZoneInfo("Asia/Manila")
    manila_time = next_run_time.astimezone(manila_tz)
    # Format as: Sunday, Nov 3, 2025 at 12:00 PM (Asia/Manila)
    return manila_time.strftime("%A, %b %d, %Y at %I:%M %p (Asia/Manila)")


# 🌈─────────────────────────────────────────────────────────────
# 💙 Minccino Scheduler Setup (setup_scheduler)
# 🌈─────────────────────────────────────────────────────────────
async def setup_scheduler(bot):

    # Start the scheduler
    scheduler_manager.start()
    schedules = []
    # ✨─────────────────────────────────────────────────────────
    # 🤍 DAILY FACTION BALL RESET — Every Midnight (NYC)
    # ✨─────────────────────────────────────────────────────────
    try:
        daily_faction_ball_reset_job = scheduler_manager.add_cron_job(
            daily_ball_reset,
            "daily_faction_ball_reset",
            hour=0,
            minute=0,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(
            daily_faction_ball_reset_job.next_run_time
        )
        schedules.append(f"Daily faction ball reset scheduled at {readable_next_run}")
        pretty_log(
            tag="background_task",
            message=f"Daily faction ball reset job scheduled at {readable_next_run}",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule daily faction ball reset job: {e}",
            bot=bot,
        )

    # ✨─────────────────────────────────────────────────────────
    # 🎯 Monthly Goal Tracker Reset — 1st of the Month at Midnight EST
    # ✨─────────────────────────────────────────────────────────
    try:
        monthly_goal_reset_job = scheduler_manager.add_cron_job(
            monthly_goal_track_reset,
            "monthly_goal_tracker_reset",
            day_of_month=1,
            hour=0,
            minute=0,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(monthly_goal_reset_job.next_run_time)
        schedules.append(f"Monthly goal tracker reset scheduled at {readable_next_run}")
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule monthly goal tracker reset job: {e}",
            bot=bot,
        )

    # ✨─────────────────────────────────────────────────────────
    # 🎯 Weekly Goal Tracker Reset Every Sunday at Midnight EST
    # ✨─────────────────────────────────────────────────────────
    try:
        weekly_goal_reset_job = scheduler_manager.add_cron_job(
            weekly_goal_track_reset,
            "weekly_goal_tracker_reset",
            day_of_week="sun",
            hour=0,
            minute=0,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(weekly_goal_reset_job.next_run_time)
        schedules.append(f"Weekly goal tracker reset scheduled at {readable_next_run}")
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule weekly goal tracker reset job: {e}",
            bot=bot,
        )

    schedule_checklist(schedules)


# 🟣────────────────────────────────────────────
#         ⚡ Startup Checklist ⚡
# 🟣────────────────────────────────────────────
def schedule_checklist(schedules):
    print("\n── · 𖨠 · ───────────────────────────────────────────────── · 𖨠 · ──")
    for schedule in schedules:
        print(f"✅ {schedule}")
    print("── · 𖨠 · ───────────────────────────────────────────────── · 𖨠 · ──\n")
