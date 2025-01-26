import io
import os
from google.cloud import vision
from googlemaps import Client as GoogleMapsClient
import wikipedia
import base64


MAPS_API_KEY = "AIzaSyBOoDCqCkmhXLzqGkXNzXir0oA1ullGG0w"


def analyze_image(image_bytes):
    try:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        if not encoded_image:
            print("Error: Image not properly encoded")
            return None

        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=encoded_image)

        response = client.label_detection(image=image)
        labels = response.label_annotations

        response = client.landmark_detection(image=image)
        landmarks = response.landmark_annotations

        return {
            "labels": [label.description for label in labels],
            "landmarks": [landmark.description for landmark in landmarks],
        }

    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None


def get_place_info(landmark):
    if landmark:
        wikipedia_info = wikipedia.summary(landmark, sentences=4)
        return wikipedia_info
    else:
        return "Sorry, I couldn't find any information about this place."


def geocode_landmark(landmark_name):
    gmaps = GoogleMapsClient(key=MAPS_API_KEY)
    try:
        geocode_result = gmaps.geocode(landmark_name)

        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return (location['lat'], location['lng'])
        else:
            print(f"Geocoding failed for landmark: {landmark_name}")
            return None

    except Exception as e:
        print(f"Error geocoding: {e}")
        return None


def find_places_nearby(latitude, longitude, query=None):
    gmaps = GoogleMapsClient(key=MAPS_API_KEY)

    try:
        if query:
            places_result = gmaps.places(query=query, location=(
                latitude, longitude), radius=500)
        else:
            places_result = gmaps.places_nearby(
                location=(latitude, longitude), radius=500)

        if places_result and places_result['results']:
            return places_result['results']
        else:
            print("No places found nearby.")
            return None

    except Exception as e:
        print(f"Error finding places: {e}")
        return None


def get_all_img(image_bytes):
    print("Starting image analysis...")

    analysis_results = analyze_image(image_bytes)
    if not analysis_results:
        print("Image analysis failed or returned no results.")
        return None

    print(f"Analysis Results: {analysis_results}")
    place_info = get_place_info(
        analysis_results['landmarks'][0] if analysis_results['landmarks'] else None)
    print(f"Place Info: {place_info}")
    return {"Place Name": analysis_results['landmarks'][0], "Place Info": place_info}


if __name__ == "__main__":
    image_path = "a.jpeg"
    get_all_img(image_path)
