from flask import Flask, render_template, request
from google.cloud import translate_v2 as translate
from livelocation import chatbot

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


if __name__ == '__main__':
    app.run(debug=True)
