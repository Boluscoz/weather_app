import requests
from django.conf import settings
from django.shortcuts import render

GEOCODE_URL = 'https://api.openweathermap.org/geo/1.0/direct'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
TIMEOUT = 10


def _fetch_weather(city, api_key):
    geo_response = requests.get(
        GEOCODE_URL,
        params={'q': city, 'limit': 1, 'appid': api_key},
        timeout=TIMEOUT,
    )
    geo_response.raise_for_status()
    results = geo_response.json()
    if not results:
        raise ValueError(f'No location found for "{city}".')

    place = results[0]
    lat = place['lat']
    lon = place['lon']

    weather_response = requests.get(
        WEATHER_URL,
        params={
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric',
        },
        timeout=TIMEOUT,
    )
    weather_response.raise_for_status()
    data = weather_response.json()

    main = data.get('main', {})
    return {
        'place': data.get('name') or place.get('name', city),
        'coordinate': f"{lat:.4f}, {lon:.4f}",
        'temperature': f"{main.get('temp', '--')} °C",
        'pressure': f"{main.get('pressure', '--')} hPa",
        'humidity': f"{main.get('humidity', '--')} %",
    }


def home(request):
    context = {}
    city = request.POST.get('location', '').strip(
    ) if request.method == 'POST' else ''

    if city:
        try:
            context.update(_fetch_weather(city, settings.OPENWEATHER_API_KEY))
        except requests.RequestException:
            context['error'] = 'Weather service is unavailable. Please try again.'
        except ValueError as exc:
            context['error'] = str(exc)

    context['city'] = city
    return render(request, 'home.html', context)
