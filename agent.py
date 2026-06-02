import json, os, httpx
from dotenv import load_dotenv

load_dotenv()

DARTMOUTH_CHAT_API_KEY = os.environ["DARTMOUTH_CHAT_API_KEY"]
BASE_URL = "https://chat.dartmouth.edu/api"
SYSTEM_PROMPT = "You are a helpful assistant."


def print_messages(messages: list) -> None:
    """Print each message in the messages array, one per line."""
    for message in messages:
        print("\t", end="")
        print(message)


def get_lat_long(zip_code: str) -> dict:
    """Return {"latitude": float, "longitude": float} for a US zip code."""
    response = httpx.get(f"https://api.zippopotam.us/us/{zip_code}")
    response.raise_for_status()
    place = response.json()["places"][0]
    return {
        "latitude": float(place["latitude"]),
        "longitude": float(place["longitude"]),
    }


def get_weather(latitude: float, longitude: float) -> dict:
    """Return current weather data for a given latitude and longitude."""
    response = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "forecast_days": 1,
            "temperature_unit": "fahrenheit",
        },
    )
    response.raise_for_status()
    data = response.json()
    current = data["current"]
    return {
        "temperature": current["temperature_2m"],
        "units": data["current_units"]["temperature_2m"],
    }


tools = {
    "get_lat_long": {
        "function": get_lat_long,
        "definition": {
            "type": "function",
            "function": {
                "name": "get_lat_long",
                "description": "Return latitude and longitude for a US zip code.",
                "parameters": {
                    "properties": {
                        "zip_code": {
                            "description": "The zip code for a US city",
                            "title": "Zip Code",
                            "type": "string",
                        }
                    },
                    "required": ["zip_code"],
                    "title": "LatLongInput",
                    "type": "object",
                },
            },
        },
    },
    "get_weather": {
        "function": get_weather,
        "definition": {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Return current weather data for a given latitude and longitude.",
                "parameters": {
                    "properties": {
                        "latitude": {
                            "description": "The latitude for a location",
                            "title": "Latitude",
                            "type": "string",
                        },
                        "longitude": {
                            "description": "The longitude for a location",
                            "title": "Longitude",
                            "type": "string",
                        },
                    },
                    "required": ["latitude", "longitude"],
                    "title": "WeatherInput",
                    "type": "object",
                },
            },
        },
    },
}


def run_agent(user_message: str, tools: dict) -> str:
    tool_definitions = [tool["definition"] for tool in tools.values()]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    while True:
        print("\nSending request to chat completions API...")
        print_messages(messages)
        response = httpx.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {DARTMOUTH_CHAT_API_KEY}"},
            json={
                "model": "google.gemma-4-31B-it",
                "messages": messages,
                "tools": tool_definitions,
            },
        )
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        tool_calls = message.get("tool_calls")

        if not tool_calls:
            return message["content"]

        messages.append(message)

        for tool_call in tool_calls:
            name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])
            print(f"Calling {name}({args})")
            result = tools[name]["function"](**args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result),
                }
            )


if __name__ == "__main__":
    reply = run_agent("What is the weather for 03755?", tools)
    print(reply)
