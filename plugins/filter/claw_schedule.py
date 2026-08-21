"""Ansible filters used by the onboarding Claw generator."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ansible.errors import AnsibleFilterError


DAY_TO_CRON = {
    "sun": 0,
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
}


def claw_morning_schedule(day_start, lead_minutes, working_days, timezone):
    """Return a five-field cron expression lead_minutes before day_start."""
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise AnsibleFilterError(f"invalid IANA timezone: {timezone}") from exc

    try:
        start = datetime.strptime(day_start, "%H:%M")
        lead = int(lead_minutes)
    except (TypeError, ValueError) as exc:
        raise AnsibleFilterError("day_start must be HH:MM and lead_minutes must be an integer") from exc
    if not 0 <= lead <= 1440:
        raise AnsibleFilterError("lead_minutes must be between 0 and 1440")

    scheduled = start - timedelta(minutes=lead)
    day_shift = (scheduled.date() - start.date()).days
    try:
        cron_days = sorted({(DAY_TO_CRON[day] + day_shift) % 7 for day in working_days})
    except (KeyError, TypeError) as exc:
        raise AnsibleFilterError("working_days contains an unsupported day") from exc
    if not cron_days:
        raise AnsibleFilterError("working_days cannot be empty")

    return {
        "cron": f"{scheduled.minute} {scheduled.hour} * * {','.join(map(str, cron_days))}",
        "timezone": timezone,
        "local_time": scheduled.strftime("%H:%M"),
    }


class FilterModule:
    """Expose role-specific schedule filters."""

    def filters(self):
        return {"claw_morning_schedule": claw_morning_schedule}
