import google.generativeai as genai
!pip install google-cloud-texttospeech
!pip install pydub
from google.cloud import texttospeech
from pydub import AudioSegment
from google.colab import files
files.upload()  # Upload the service account JSON key file

# Set the environment variable to point to your key file
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "projectrit-bb9d783f6699.json"
# Configure the API
genai.configure(api_key="AIzaSyCjsqbMcPSRUrDjAyiP4A8UfKiI75FizG0")

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')
import os
import google.generativeai as genai
from google.cloud import texttospeech
from pydub import AudioSegment
!pip install SpeechRecognition
import speech_recognition as sr
from google.colab import files

# Configure Google GenAI
genai.configure(api_key="AIzaSyAsWu_wDY6U42pultcpIWheo8y0cSJAD4c")
model = genai.GenerativeModel("gemini-1.5-flash")

# Configure Google Cloud Text-to-Speech
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "projectrit-bb9d783f6699.json"

def synthesize_speech(text):
    """Convert text to speech and save as MP3."""
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)

    # Configure voice and audio settings
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Generate speech
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # Save the output as MP3
    with open("response.mp3", "wb") as out:
        out.write(response.audio_content)
    print("Audio content saved as response.mp3")
    files.download("response.mp3")  # Download the file for playback

def get_genai_response(prompt):
    """Generate a response using Google GenAI."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error with GenAI API: {str(e)}"

def transcribe_audio(audio_path):
    """Transcribe audio file using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        print("Processing audio...")
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "I couldn't understand the audio."
        except sr.RequestError:
            return "Error connecting to the speech service."

# Upload the service account JSON key file
files.upload()

# Main Execution
synthesize_speech("Hello! Please upload an audio file for me to process.")
print("Upload your audio file:")
uploaded = files.upload()  # Upload your audio file

if uploaded:
    audio_file = list(uploaded.keys())[0]
    user_input = transcribe_audio(audio_file)
    print(f"You said: {user_input}")
    if "stop" in user_input:
        synthesize_speech("Goodbye!")
    else:
        response = get_genai_response(user_input)
        print(f"Response: {response}")
        synthesize_speech(response)
