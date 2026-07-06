from datetime import datetime, timedelta

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

_HEAVY_RAIN_CODES = {65, 82}
_RAIN_CODES = {63, 66, 67, 80, 81}
_STORM_CODES = {95, 96, 99}
_HIGH_WIND_KMH = 40


def _alert_message(code: int, windspeed: float) -> str | None:
    if code in _STORM_CODES:
        return "⛈️ Orage prévu"
    if code in _HEAVY_RAIN_CODES:
        return "🌧️ Pluies très fortes prévues"
    if code in _RAIN_CODES:
        return "🌧️ Fortes pluies prévues"
    if windspeed >= _HIGH_WIND_KMH:
        return "💨 Vents violents prévus"
    return None


async def get_weather_alert(city: str, country: str) -> dict | None:
    """Cherche dans les prévisions horaires des prochaines 24h la première alerte
    de mauvais temps (orage, fortes pluies, vents violents). Retourne None si RAS."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            geo = await client.get(GEOCODING_URL, params={"name": city, "count": 1, "language": "fr"})
            geo.raise_for_status()
            results = geo.json().get("results")
            if not results:
                return None
            lat, lon = results[0]["latitude"], results[0]["longitude"]

            forecast = await client.get(
                FORECAST_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": "weathercode,windspeed_10m",
                    "forecast_days": 2,
                    "timezone": "auto",
                },
            )
            forecast.raise_for_status()
            hourly = forecast.json()["hourly"]

            now = datetime.now()
            horizon = now + timedelta(hours=24)
            for time_str, code, wind in zip(hourly["time"], hourly["weathercode"], hourly["windspeed_10m"]):
                hour_dt = datetime.fromisoformat(time_str)
                if hour_dt < now or hour_dt > horizon:
                    continue
                message = _alert_message(int(code), float(wind))
                if message:
                    return {"message": message, "expected_time": hour_dt.strftime("%H:%M")}
            return None
        except Exception:
            return None
