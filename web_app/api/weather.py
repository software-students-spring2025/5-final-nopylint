import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime
from pytz import timezone as pytz_timezone
from raspberry_pi.agent import get_system_metrics
import pandas as pd

def get_current_weather_ny():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 40.692944,
        "longitude": -73.987086,
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "America/New_York",
        "past_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    temps = hourly.Variables(0).ValuesAsNumpy()
    hums = hourly.Variables(1).ValuesAsNumpy()
    dates = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )
    df = pd.DataFrame({
        "date": dates,
        "temperature_2m": temps,
        "relative_humidity_2m": hums
    })
    ny_tz = pytz_timezone("America/New_York")
    now_ny = datetime.now(ny_tz).replace(minute=0, second=0, microsecond=0)
    row = df[df['date'] == now_ny]
    if not row.empty:
        temp = float(row['temperature_2m'].values[0])
        humidity = float(row['relative_humidity_2m'].values[0])
        return round(temp, 2), round(humidity, 2)
    return None, None

def get_weather_summary():
    sensor = get_system_metrics()
    env_temp = sensor.get('temperature')
    env_humidity = sensor.get('humidity')
    regional_temp, regional_humidity = get_current_weather_ny()
    suggestion = ''
    if env_temp is not None:
        if env_temp >= 30:
            suggestion = 'Environment is hot. Consider cooling.'
        elif env_temp <= 15:
            suggestion = 'Environment is cold. Consider heating.'
        else:
            suggestion = 'Environment temperature is comfortable.'
    return {
        'env_temp': env_temp,
        'env_humidity': env_humidity,
        'regional_temp': regional_temp,
        'regional_humidity': regional_humidity,
        'suggestion': suggestion
    }

def main():
    summary = get_weather_summary()
    print(summary)

if __name__ == '__main__':
    main()
