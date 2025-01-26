from flask import Flask, render_template, request, jsonify
from google.cloud import translate_v2 as translate
from livelocation import chatbot
from trip_planning import generate_trip_plan
from image import get_all_img


app = Flask(__name__)

translate_client = translate.Client()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/get", methods=["POST"])
def translate_and_chat():
    user_msg = request.form.get("msg")

    if not user_msg:
        return "Error: No input received", 400

    detection_result = translate_client.detect_language(user_msg)
    detected_lang = detection_result['language']

    if detected_lang != "en":
        translated_input = translate_client.translate(
            user_msg, target_language="en")['translatedText']
    else:
        translated_input = user_msg

    bot_response_in_english = chatbot(translated_input)

    if detected_lang != "en":
        translated_response = translate_client.translate(
            bot_response_in_english, target_language=detected_lang)['translatedText']
    else:
        translated_response = bot_response_in_english

    return translated_response


@app.route("/plan")
def plan():
    return render_template('plantour.html')


@app.route("/plantour", methods=["GET", "POST"])
def plantour():
    if request.method == "POST":
        destination = request.form.get("destination")
        origin = request.form.get("origin")
        departure_date = request.form.get("departure_date")
        suggestions = request.form.get("suggestions")
        response = generate_trip_plan(
            destination, origin, departure_date, suggestions)
        return response


@app.route("/image")
def image():
    return render_template('image.html')


@app.route("/imageupload", methods=["POST"])
def imageupload():
    uploaded_file = request.files.get("image")
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    image_bytes = uploaded_file.read()
    if not image_bytes:
        return jsonify({"error": "File is empty"}), 400

    get_info = get_all_img(image_bytes)
    if get_info is None:
        return jsonify({"error": "Image processing failed"}), 500

    return str(get_info)


if __name__ == '__main__':
    app.run(debug=True)
