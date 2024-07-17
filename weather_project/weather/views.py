import logging
import pandas as pd
import requests
import requests_cache
from django.http import JsonResponse
from django.shortcuts import render
from retry_requests import retry
import pytz
from datetime import datetime, timedelta

from .forms import CityForm
import openmeteo_requests

# Настройка кеширования и повторных попыток запросов
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Настройка логирования
logger = logging.getLogger(__name__)

def get_city_coordinates(city):
    """Получает координаты города по его названию"""
    try:
        response = requests.get(f'https://nominatim.openstreetmap.org/search?q={city}&format=json')
        if response.status_code == 200:
            data = response.json()
            if data:
                logger.info(f"Coordinates for {city}: {data[0]['lat']}, {data[0]['lon']}")
                return float(data[0]['lat']), float(data[0]['lon'])
            else:
                logger.warning(f"No data found for city: {city}")
        else:
            logger.error(f"Failed to get coordinates for city: {city}, status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error getting coordinates for city: {city}, {e}")
    return None, None

def get_weather_data(latitude, longitude):
    """Получает погодные данные для заданных координат"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "timezone": "UTC",
        "models": "jma_seamless"
    }
    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        
        # Получаем текущее время в часовой зоне UTC+3 (МСК)
        now_msk = datetime.now(pytz.timezone('Europe/Moscow'))
        
        # Фильтруем данные, чтобы показать прогноз на следующие 12 часов
        start_time_utc = now_msk.astimezone(pytz.utc)
        end_time_utc = start_time_utc + timedelta(hours=12)
        
        hourly_data = {
            "Время": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "Температура": hourly_temperature_2m
        }
        df = pd.DataFrame(data=hourly_data)
        
        # Фильтрация данных по времени
        df = df[(df['Время'] >= start_time_utc) & (df['Время'] < end_time_utc)]
        
        # Преобразование времени и температуры в удобный формат
        df['Температура'] = df['Температура'].round().astype(int).astype(str) + '°C'
        df['Время'] = df['Время'].dt.tz_convert('Europe/Moscow').dt.strftime('%H:%M')
        
        logger.info(f"Weather data for coordinates {latitude}, {longitude} successfully retrieved.")
        return df
    except Exception as e:
        logger.error(f"Failed to get weather data for coordinates {latitude}, {longitude}. Error: {e}")
        return pd.DataFrame()

def weather_view(request):
    """
    Обрабатывает запросы к веб-приложению для отображения формы ввода города и погодных данных для этого города.
    """
    if request.method == 'POST' and 'autocomplete' in request.POST:
        query = request.POST.get('city', '')
        response = requests.get(f'https://nominatim.openstreetmap.org/search?q={query}&format=json')
        if response.status_code == 200:
            data = response.json()
            results = [{'label': item['display_name'], 'value': item['display_name']} for item in data]
            return JsonResponse(results, safe=False)
        return JsonResponse([], safe=False)
    
    elif request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            latitude, longitude = get_city_coordinates(city)
            if latitude and longitude:
                weather_data = get_weather_data(latitude, longitude)
                return render(request, 'weather/weather.html', {'form': form, 'weather_data': weather_data.to_html(index=False)})
            else:
                logger.warning(f"Failed to get coordinates for city: {city}")
                return render(request, 'weather/weather.html', {'form': form, 'error': f'Could not find coordinates for the city {city}.'})
    else:
        form = CityForm()
        logger.info("GET request received, rendering form.")
    return render(request, 'weather/weather.html', {'form': form})
