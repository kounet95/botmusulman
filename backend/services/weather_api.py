from datetime import datetime, timedelta

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Regroupement simplifié des codes météo WMO (open-meteo.com/en/docs)
WMO_ICONS = {
    0: ("☀️", "Ciel dégagé"),
    1: ("🌤️", "Plutôt dégagé"),
    2: ("⛅", "Partiellement nuageux"),
    3: ("☁️", "Couvert"),
    45: ("🌫️", "Brouillard"),
    48: ("🌫️", "Brouillard givrant"),
    51: ("🌦️", "Bruine légère"),
    53: ("🌦️", "Bruine"),
    55: ("🌦️", "Bruine forte"),
    61: ("🌧️", "Pluie légère"),
    63: ("🌧️", "Pluie"),
    65: ("🌧️", "Pluie forte"),
    71: ("🌨️", "Neige légère"),
    73: ("🌨️", "Neige"),
    75: ("❄️", "Neige forte"),
    80: ("🌦️", "Averses"),
    81: ("🌧️", "Averses fortes"),
    82: ("⛈️", "Averses violentes"),
    95: ("⛈️", "Orage"),
}

# Codes considérés comme du "mauvais temps" (saison des pluies / orages à Conakry)
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


async def _geocode(client: httpx.AsyncClient, city: str) -> tuple[float, float] | None:
    geo = await client.get(GEOCODING_URL, params={"name": city, "count": 1, "language": "fr"})
    geo.raise_for_status()
    results = geo.json().get("results")
    if not results:
        return None
    return results[0]["latitude"], results[0]["longitude"]


async def get_weather(city: str, country: str) -> dict | None:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            coords = await _geocode(client, city)
            if not coords:
                return None
            lat, lon = coords

            forecast = await client.get(
                FORECAST_URL,
                params={"latitude": lat, "longitude": lon, "current_weather": "true"},
            )
            forecast.raise_for_status()
            current = forecast.json()["current_weather"]
            icon, condition = WMO_ICONS.get(int(current["weathercode"]), ("🌡️", "—"))
            return {
                "temperature": round(current["temperature"]),
                "icon": icon,
                "condition": condition,
            }
        except Exception:
            return None


async def get_weather_alert(city: str, country: str) -> dict | None:
    """Cherche dans les prévisions horaires des prochaines 24h la première alerte
    de mauvais temps (orage, fortes pluies, vents violents). Retourne None si RAS."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            coords = await _geocode(client, city)
            if not coords:
                return None
            lat, lon = coords

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
