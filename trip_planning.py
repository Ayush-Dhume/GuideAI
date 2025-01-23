import requests
from datetime import datetime, timedelta
import google.generativeai as genai


def generate_trip_plan(destination, origin, departure_date, suggestions):
    """Generate a detailed trip plan."""
    try:
        prompt = (f"Create a detailed and practical trip itinerary for a traveler going from {origin} to {destination} on {departure_date}. "
                  "The itinerary should include the following details:\n"
                  "- Recommended flights with timings and estimated costs.\n"
                  "- Suggested accommodations with price ranges and locations.\n"
                  "- A list of must-visit attractions or historical sites in the destination.\n"
                  "- Weather forecast for the duration of the trip.\n"
                  "- Any additional travel tips or recommendations for dining, transport, and local culture."
                  "- In simple font no bold or italic etc."
                  f"Take the user suggestions into consideration for the plan: {suggestions}")
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate response
        response = model.generate_content(prompt)
        if response:
            return response.text
        else:
            return "Could'nt make a plan!"
    except Exception as e:
        print(f"Could'nt make a plan!: {e}")
        return "Could'nt make a plan!"


if __name__ == "__main__":
    destination = input("Enter your destination: ")
    origin = input("Enter your origin: ")
    departure_date = input("Enter your departure date (YYYY-MM-DD): ")
    suggestions = input("Any Suggestions?: ")
    bot_response = generate_trip_plan(
        destination, origin, departure_date, suggestions)
    print(bot_response)
