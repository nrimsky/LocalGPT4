import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
import random

load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")


def fetch_weather_data(location):
    lat, lon = location
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data["weather"][0]["description"], data["main"]["temp"]


def fetch_city_name(location):
    lat, lon = location
    url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={OPENCAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    city = data['results'][0]['components']['city']
    return city

def fetch_local_news(city):
    url = f"https://newsapi.org/v2/everything?q={city}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'ok':
        return data['articles'][:3]
    else:
        return []


def fetch_venues(location):
    interesting_queries = [
        "museum",
        "landmark",
        "art gallery",
        "theater",
        "historical site",
        "park",
        "scenic viewpoint",
        "monument",
        "street art",
        "live music",
        "brewery",
        "unique cafe",
    ]
    query = random.choice(interesting_queries)

    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "accept": "application/json",
        "Authorization": f"{FOURSQUARE_API_KEY}",
    }
    params = {
        "ll": f"{location[0]},{location[1]}",
        "query": query,
        "limit": 6,  # You can adjust the limit as needed
    }

    response = requests.get(url, headers=headers, params=params)
    venues = response.json()["results"]

    return venues, query

def fetch_wikipedia_data(location):
    latitude, longitude = location
    radius = 1200  # Radius in meters; you can adjust this as needed.

    wikipedia_api_url = f"https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "geosearch",
        "gscoord": f"{latitude}|{longitude}",
        "gsradius": radius,
        "gslimit": 6,  # Limit the number of results; adjust as needed.
    }

    response = requests.get(wikipedia_api_url, params=params)

    if response.status_code == 200:
        wikipedia_data = response.json()
        titles = [result["title"] for result in wikipedia_data["query"]["geosearch"]]
        return titles
    else:
        raise Exception(f"Error fetching Wikipedia data: {response.status_code}")

def construct_llm_prompt(location, timezone):
    weather_description, temperature = fetch_weather_data(location)
    city = fetch_city_name(location)
    local_news = fetch_local_news(city)
    venues, query = fetch_venues(location)
    wiki_data = fetch_wikipedia_data(location)

    now = datetime.now(pytz.timezone(timezone))
    local_time = now.strftime("%Y-%m-%d %H:%M:%S")

    prompt = f"Here is some info on the local area.\nAt {local_time} in {city}, the weather is {weather_description} with a temperature of {temperature}°C.\nHere are some local news headlines:\n"
    for article in local_news:
        prompt += f"- {article['title']}\n"

    prompt += "Some interesting things nearby are:\n"
    for item in wiki_data:
        prompt += f"- {item}\n"

    prompt += f"Nearby cool {query}s include:\n"
    for venue in venues:
        if len(venue.get('categories', [])) == 0:
            venue['categories'] = [{'name': 'uncategorized'}]
        prompt += (
            f"- {venue['name']} ({venue['categories'][0]['name']})\n"
        )
    prompt += "Now please generate the script"

    return prompt


if __name__ == "__main__":
    # Example usage
    location = (51.5074, -0.1278)  # London, UK
    timezone = "Europe/London"
    llm_prompt = construct_llm_prompt(location, timezone)
    print(llm_prompt)
