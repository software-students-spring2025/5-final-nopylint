import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime
from pytz import timezone as pytz_timezone


def get_current_weather_ny():
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

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
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly_temperature_2m,
        "relative_humidity_2m": hourly_relative_humidity_2m
    }

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    ny_tz = pytz_timezone("America/New_York")
    now_ny = datetime.now(ny_tz).replace(minute=0, second=0, microsecond=0)

    current_row = hourly_dataframe[hourly_dataframe['date'] == now_ny]
    if not current_row.empty:
        temp = float(current_row["temperature_2m"].values[0])
        humidity = float(current_row["relative_humidity_2m"].values[0])
        return round(temp, 2), round(humidity, 2)
    else:
        return None, None

def main():
    temp, humidity = get_current_weather_ny()
    print(f"Current (New York) - Temperature: {temp}°C, Humidity: {humidity}%")

if __name__ == "__main__":
    main()