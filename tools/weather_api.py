import os
import requests
from datetime import datetime
from config import settings

class WeatherTool:
    def __init__(self):
        # .env loaded via config.settings import side-effect
        self.api_key = settings.require_env(settings.OPENWEATHER_API_KEY, "OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "https://api.openweathermap.org/geo/1.0"

    def _geocode_city(self, city_name):
        try:
            url = f"{self.geo_url}/direct"
            params = {
                "q": city_name,
                "limit": 1,
                "appid": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return None, None
            
            # Get first result
            location = data[0]
            return location['lat'], location['lon']
            
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None, None

    def _fetch_forecast(self, lat, lon):

        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"  # celsius
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()

    def get_forecast(self, city_name):
        try:
            lat, lon = self._geocode_city(city_name)
            if lat is None or lon is None:
                print(f"Could not geocode city: {city_name}")
                return []
            
            forecast_data = self._fetch_forecast(lat, lon)

            normalized = self._normalize_forecast(forecast_data)
            return normalized
        except Exception as e:
            print(f"Weather forecast error: {e}")
            return []

    def _normalize_forecast(self, raw_data):
        #convert raw API response to our standard format

        if 'list' not in raw_data:
            return []
        
        # OpenWeatherMap returns 3-hour intervals
        # we need to aggregate by day
        daily_data = {}
        
        for item in raw_data['list']:
            # parse date
            dt = datetime.fromtimestamp(item['dt'])
            date_key = dt.strftime('%Y-%m-%d')
            
            # extract temperature
            temp = item['main']['temp']
            temp_min = item['main']['temp_min']
            temp_max = item['main']['temp_max']
            description = item['weather'][0]['description'] if item['weather'] else ""
            
            # aggregate by day
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'date': date_key,
                    'temps': [],
                    'temp_mins': [],
                    'temp_maxs': [],
                    'descriptions': []
                }
            
            daily_data[date_key]['temps'].append(temp)
            daily_data[date_key]['temp_mins'].append(temp_min)
            daily_data[date_key]['temp_maxs'].append(temp_max)
            daily_data[date_key]['descriptions'].append(description)
        
        # calculate daily min/max and pick most common description
        normalized = []
        
        for date_key in sorted(daily_data.keys())[:7]:  # Limit to 7 days
            day = daily_data[date_key]
            
            normalized.append({
                'date': day['date'],
                'temp_min': round(min(day['temp_mins']), 1),
                'temp_max': round(max(day['temp_maxs']), 1),
                'temp_avg': round(sum(day['temps']) / len(day['temps']), 1),
                'description': max(set(day['descriptions']), key=day['descriptions'].count)
            })
        
        return normalized
    

