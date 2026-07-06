import httpx
from datetime import datetime
import pytz

ALADHAN_BASE = "https://api.aladhan.com/v1"

PRAYER_NAMES = {
    "Fajr": "Fajr 🌙",
    "Sunrise": "Lever du soleil 🌅",
    "Dhuhr": "Dhuhr ☀️",
    "Asr": "Asr 🌤️",
    "Maghrib": "Maghrib 🌇",
    "Isha": "Isha 🌙",
}


async def get_prayer_times(city: str, country: str, date: str | None = None) -> dict | None:
    if not date:
        date = datetime.now().strftime("%d-%m-%Y")
    url = f"{ALADHAN_BASE}/timingsByCity/{date}"
    params = {"city": city, "country": country, "method": 2}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            return data["data"]["timings"]
        except Exception:
            return None


def format_prayer_times(timings: dict, city: str) -> str:
    today = datetime.now().strftime("%A %d %B %Y")
    lines = [
        f"🕌 *Horaires de prière — {city}*",
        f"📅 {today}",
        "━━━━━━━━━━━━━━━━━━",
    ]
    for key, label in PRAYER_NAMES.items():
        if key in timings:
            lines.append(f"{label} — *{timings[key]}*")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("_Que Allah accepte vos prières_ 🤲")
    return "\n".join(lines)


async def get_next_prayer(city: str, country: str) -> tuple[str, str] | None:
    timings = await get_prayer_times(city, country)
    if not timings:
        return None
    now = datetime.now()
    prayer_order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    for name in prayer_order:
        if name not in timings:
            continue
        h, m = map(int, timings[name].split(":"))
        prayer_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if prayer_dt > now:
            return name, timings[name]
    return "Fajr", timings.get("Fajr", "")
