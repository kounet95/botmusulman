from datetime import datetime

import httpx

ALADHAN_BASE = "https://api.aladhan.com/v1"
PRAYER_ORDER = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]


async def get_prayer_times(city: str, country: str) -> dict | None:
    date = datetime.now().strftime("%d-%m-%Y")
    url = f"{ALADHAN_BASE}/timingsByCity/{date}"
    params = {"city": city, "country": country, "method": 2}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()["data"]
            timings = {k: v.split(" ")[0] for k, v in data["timings"].items()}
            return {
                "timings": {k: v for k, v in timings.items() if k in PRAYER_ORDER},
                "sunrise": timings.get("Sunrise"),
                "gregorian_date": data["date"]["readable"],
                "hijri_date": f"{data['date']['hijri']['day']} {data['date']['hijri']['month']['en']} {data['date']['hijri']['year']}",
            }
        except Exception:
            return None


def get_next_prayer(timings: dict) -> dict:
    now = datetime.now()
    for name in PRAYER_ORDER:
        if name not in timings:
            continue
        h, m = map(int, timings[name].split(":"))
        prayer_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if prayer_dt > now:
            return {"name": name, "time": timings[name]}
    return {"name": "Fajr", "time": timings.get("Fajr", "")}
