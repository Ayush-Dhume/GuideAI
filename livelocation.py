import requests
import google.generativeai as genai
import json
import googlemaps
import random
from google.generativeai import client
from ibm_watson import SpeechToTextV1, TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import (
    Features,
    EntitiesOptions,
    KeywordsOptions,
)

service_url = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/59a06cdd-c88a-41b7-89da-7d023a38429a"
authenticator = IAMAuthenticator(
    "HZ23cQEFij1oYhodDYhViIzyexLMiRvAqBrnXl7gkAUg")
nlu = NaturalLanguageUnderstandingV1(
    version="2022-04-07", authenticator=authenticator)
nlu.set_service_url(service_url)

gemini_key = "AIzaSyCBqyD8j_HspxNryOM1Qqeu-hoAjNfgdMo"
google_api_key = "AIzaSyBOoDCqCkmhXLzqGkXNzXir0oA1ullGG0w"

genai.configure(api_key=gemini_key)


def detect_intent_and_respond(query):
    try:
        # Prompt engineering for intent detection
        prompt = f"""
        The user query is: "{query}".
        Identify the intent of the query and give only intent in plain text.
        Possible intents: self_Location Inquiry, Trip Planning, Place Details, Activity Suggestions,
        Navigation Help, Language Translation, General Help, Nearby location Inquiry(A to B), Nearby location Inquiry.
        """

        # Create the model instance
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate response
        response = model.generate_content(prompt)
        if response:
            return response.text.strip()  # Ensure clean response
        else:
            return "Unknown Intent"
    except Exception as e:
        print(f"Error detecting intent: {e}")
        return "Error in detecting intent"


# fallback if intent does'nt match
def fallback_response():
    fallback_responses = [
        "Oops! My brain just did a backflip. Can you try asking that again?",
        "Beep boop... I'm officially confused. Can you break it down for me?",
        "Sorry, I missed that. I was busy daydreaming about a vacation. What was it again?",
        "Hmm... I might need more coffee to understand that. Try again?",
        "I think my wires got tangled. Let’s rewind and try again!",
    ]
    return random.choice(fallback_responses)

# match entity with google places


def match_entity_with_google_places(entity):
    try:
        # Prompt engineering for intent detection
        prompt = f"""
        The entity is: "{entity}".
        Match the entity with any of the given google places keys(just give one key as answer):
        "accounting",
    "airport",
    "amusement_park",
    "aquarium",
    "art_gallery",
    "atm",
    "bakery",
    "bank",
    "bar",
    "beauty_salon",
    "bicycle_store",
    "book_store",
    "bowling_alley",
    "bus_station",
    "cafe",
    "campground",
    "car_dealer",
    "car_rental",
    "car_repair",
    "car_wash",
    "casino",
    "cemetery",
    "church",
    "city_hall",
    "clothing_store",
    "colloquium",
    "convenience_store",
    "courthouse",
    "dentist",
    "department_store",
    "doctor",
    "electrician",
    "electronics_store",
    "embassy",
    "fire_station",
    "florist",
    "food",
    "funeral_home",
    "furniture_store",
    "gas_station",
    "gym",
    "hair_care",
    "hardware_store",
    "health",
    "hindu_temple",
    "home_goods_store",
    "hospital",
    "insurance_agency",
    "jewelry_store",
    "laundry",
    "lawyer",
    "library",
    "liquor_store",
    "local_government_office",
    "locksmith",
    "lodging",
    "meal_delivery",
    "meal_takeaway",
    "mosque",
    "movie_rental",
    "movie_theater",
    "moving_company",
    "museum",
    "night_club",
    "other",
    "park",
    "parking",
    "pet_store",
    "pharmacy",
    "physiotherapist",
    "plumber",
    "police",
    "post_office",
    "primary_school",
    "real_estate_agency",
    "restaurant",
    "roofing_contractor",
    "school",
    "secondary_school",
    "shoe_store",
    "shopping_mall",
    "spa",
    "stadium",
    "storage",
    "store",
    "subway_station",
    "supermarket",
    "synagogue",
    "taxi_stand",
    "tourist_attraction",
    "train_station",
    "transit_station"
        """

        # Create the model instance
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate response
        response = model.generate_content(prompt)
        if response:
            return response.text.strip()  # Ensure clean response
        else:
            return "Unknown place"
    except Exception as e:
        print(f"Error detecting place: {e}")
        return "Error in detecting place"


# detect the entities and keywords
def extract_entities_and_keywords(user_query):
    response = nlu.analyze(
        text=user_query,
        features=Features(
            entities=EntitiesOptions(sentiment=True, emotion=True),
            keywords=KeywordsOptions(sentiment=True, emotion=True),
        ),
    ).get_result()

    # Extract entities and keywords
    entities = [
        {"text": entity["text"], "type": entity["type"]}
        for entity in response.get("entities", [])
    ]
    keywords = [keyword["text"] for keyword in response.get("keywords", [])]

    return entities, keywords


# Self-location Enquiry as an intent.
def get_current_location(google_api_key):
    try:
        url = (
            f"https://www.googleapis.com/geolocation/v1/geolocate?key={
                google_api_key}"
        )
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers)
        data = response.json()
        print("API Response:", data)

        if "location" in data and data["location"]:
            lat = data["location"]["lat"]
            lng = data["location"]["lng"]
            return lat, lng
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def get_address_from_coordinates(google_api_key, lat, lng):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lng}",
        "key": google_api_key,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data["status"] == "OK":
            # Select the most relevant address
            results = data["results"]
            if results:
                # Get the first address
                address = results[0].get("formatted_address")
                return address
            else:
                print("No results found for the given coordinates.")
                return None
        elif data["status"] == "ZERO_RESULTS":
            print("No results found for the given coordinates.")
            return None
        else:
            print(f"Geocoding API error: {data.get('status', 'Unknown')}, Error: {
                  data.get('error_message', 'No error message')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return None
    except KeyError as e:
        print(f"A key error occurred when parsing the response: {
              e}. Ensure correct API output structure.")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse API response as JSON: {e}")
        return None


# search nearby places
def search_nearby_places(
    api_key, latitude, longitude, place_type, radius=5000, keyword=None
):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "key": api_key,
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "type": place_type,
        "rankby": "prominence",
    }
    if keyword:
        params["keyword"] = keyword

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            return data["results"]
        else:
            print(f"Google Places API Error: {data.get('status', 'Unknown')}")
            print(f"Error Message: {
                  data.get('error_message', 'No error message')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network or Request Error: {e}")
        return None


def get_nearby_attractions(google_api_key, lat, lng):
    # Use the Google Places API to get nearby attractions
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={
        lat},{lng}&radius=5000&types=point_of_interest&key={google_api_key}"
    response = requests.get(url)
    data = response.json()

    if data["results"]:
        attractions = [result["name"] for result in data["results"]]
        return attractions
    else:
        return None


def get_directions(google_api_key, lat, lng):
    # Use the Google Directions API to get directions
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={
        lat},{lng}&destination=landmark&key={google_api_key}"
    response = requests.get(url)
    data = response.json()

    if data["routes"]:
        directions = data["routes"][0]["legs"][0]["steps"]
        return directions
    else:
        return None


def get_place_details(query):
    try:
        prompt = f"give breif introduction {query} in plain text"

        model = genai.GenerativeModel("gemini-1.5-flash")
        ai_response = model.generate_content(prompt)

        if ai_response:
            description = ai_response.text.strip()
        else:
            description = "No description available for this place."

        response_text = (
            f"{description}"
        )

        return response_text

    except requests.exceptions.RequestException as e:
        return f"Error fetching place details: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


def chatbot(user_query):
    try:
        intent = detect_intent_and_respond(user_query)
        response = ""

        if intent == "self_Location Inquiry":
            current_location = get_current_location(google_api_key)
            if current_location:
                lat, lng = current_location
                address = get_address_from_coordinates(
                    google_api_key, lat, lng)
                response = f"You are currently located at {address}."
            else:
                response = "Unable to fetch your current location."

        elif intent == "Nearby location Inquiry(A to B)":
            current_location = get_current_location(google_api_key)
            if current_location:
                lat, lng = current_location
                attractions = get_nearby_attractions(google_api_key, lat, lng)
                response = (
                    f"Nearby attractions: {', '.join(attractions)}"
                    if attractions
                    else "No attractions found."
                )

        elif intent == "Navigation Help":
            current_location = get_current_location(google_api_key)
            if current_location:
                lat, lng = current_location
                directions = get_directions(google_api_key, lat, lng)
                response = (
                    f"Directions: {' '.join(directions)}"
                    if directions
                    else "No directions found."
                )

        elif intent == "Nearby location Inquiry":
            current_location = get_current_location(google_api_key)
            entity = extract_entities_and_keywords(user_query)
            str_entity = "".join(entity[1])
            place_type = match_entity_with_google_places(str_entity)
            if current_location:
                lat, lng = current_location
                places = search_nearby_places(
                    google_api_key, lat, lng, place_type, 1000
                )
                if places:
                    response = f"<b>Here are some nearby {
                        str_entity}:</b><br><ul>"
                    for place in places:
                        name = place.get("name", "N/A")
                        address = place.get("vicinity", "N/A")
                        rating = place.get("rating", "N/A")
                        response += (
                            f"<li><b>Name:</b> {name}<br>"
                            f"<b>Address:</b> {address}<br>"
                            f"<b>Rating:</b> {rating}</li><br>"
                        )
                        response += "</ul>"
                else:
                    response = (f"Sorry! There is no {str_entity} near you!")

        elif intent == "Place Details":
            entities = extract_entities_and_keywords(user_query)
            print(entities[0])
            response = get_place_details(user_query)

        else:
            response = fallback_response()
        return response
    except Exception as e:
        print(f"Error in chatbot logic: {e}")
        return "An error occurred while processing your query."


if __name__ == "__main__":
    user_query = input("Ask your question: ")
    bot_response = chatbot(user_query)
    print(bot_response)
