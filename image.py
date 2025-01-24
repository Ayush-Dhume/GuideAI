import io
import os
from google.cloud import vision
from googlemaps import Client as GoogleMapsClient
import wikipedia

MAPS_API_KEY = "AIzaSyBOoDCqCkmhXLzqGkXNzXir0oA1ullGG0w"


def analyze_image(image_path):
    try:
        client = vision.ImageAnnotatorClient()

        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

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


if __name__ == "__main__":
    image_path = "a.jpeg"

    analysis_results = analyze_image(image_path)
    place_info = get_place_info(analysis_results['landmarks'])

    if analysis_results:
        print("Image Analysis Results:")
        print(f"Labels: {analysis_results['labels']}")
        print(f"Landmarks: {analysis_results['landmarks']}")
        print(place_info)

        if analysis_results['landmarks']:
            landmark_name = analysis_results['landmarks'][0]
            coordinates = geocode_landmark(landmark_name)

            if coordinates:
                print(f"Geocoded coordinates for {
                      landmark_name}: {coordinates}")
                places = find_places_nearby(coordinates[0], coordinates[1])

                if places:
                    print("\nNearby Places:")
                    for place in places:
                        print(f"- {place['name']} ({place['geometry']['location']
                              ['lat']}, {place['geometry']['location']['lng']})")
                else:
                    print("Could not find any places nearby the geocoded coordinates.")

        elif analysis_results['full_text']:
            full_text_query = analysis_results['full_text']
            landmark_coordinates = geocode_landmark(full_text_query)
            if landmark_coordinates:
                places = find_places_nearby(
                    landmark_coordinates[0], landmark_coordinates[1])
                if places:
                    print("\nNearby Places (from text):")
                    for place in places:
                        print(f"- {place['name']} ({place['geometry']['location']
                              ['lat']}, {place['geometry']['location']['lng']})")
                else:
                    print(
                        "Could not find any places nearby the geocoded coordinates (from text).")
            else:
                print("Could not geocode the text.")

        else:
            print("No landmarks or text found in the image.")
    else:
        print("Image analysis failed.")
