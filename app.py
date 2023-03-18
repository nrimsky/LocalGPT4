# app.py
from flask import Flask, send_from_directory, request, jsonify
from gtts import gTTS
import os
import openai
import io
import base64
from dotenv import load_dotenv
from getprompt import construct_llm_prompt


# Set up OpenAI API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__, static_folder="build", static_url_path="/")

SYSTEM_PROMPT = """
You are a tool that generates content for a funny, interesting, and entertaing podcast about the local area. 
The podcast has a single host. 
Your job is to provide the script *verbatim*, without any additional annotations (no need to write 'Host:' or similar!). 
You never produce intros, outros, or filler content. 
You occassionally make it clear that the content was AI generated, but do so in a funny and cute way (sound like a self-aware AI).
Users will provide you with some research they have done on the local area, and your job is to synthesise this and summarise this into a 2 to 3 minute script.
You are completely allowed to miss out some bits of the research if you think there won't be enough time to include them as part of a coherent text.
Also, please miss out any controversial news headlines or items that could cause offence.
Finally, make sure to make a few spicy jokes and keep the tone light. The aim is to entertain! Don't sound overly didactic or like a tour guide.
"""


@app.route("/api/generate-podcast", methods=["POST"])
def generate_podcast():
    location = request.json["location"]
    timezone = "Europe/London"
    prompt = construct_llm_prompt((location["latitude"], location["longitude"]), timezone)
    openai_response = generate_openai_response(prompt)
    audio_base64 = text_to_speech(openai_response)

    return jsonify({"audio": audio_base64})


def generate_openai_response(prompt):
    # Make a request to the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=600,  # Adjust the length of the response as needed
        n=1,
        stop="goodbye!",
        temperature=0.8,
    )

    generated_text = response.choices[0]["message"]["content"].strip() + " goodbye!"

    return generated_text


def text_to_speech(text):
    # Create a gTTS object with the text
    tts = gTTS(text, lang="en")

    # convert to file-like object
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    audio_base64 = base64.b64encode(fp.read()).decode("utf-8")

    return audio_base64


# Add Serve the static files from the React app's build folder


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static_files(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(debug=True)
