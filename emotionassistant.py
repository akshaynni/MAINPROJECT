import cv2
import time
import re
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from fer import FER

# Configure Google GenAI API
genai.configure(api_key="AIzaSyAmqZZJmHn-m7uaxfixuZhjIGOwdXFJBbI")
model = genai.GenerativeModel("gemini-1.5-flash")  # Correct API usage

# Initialize emotion detector
detector = FER()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to speak out messages
def speak(text):
    print("Neo:", text)  # Display response
    engine.say(text)
    engine.runAndWait()

# Function to listen to user input with better noise handling
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)  # Adjust for background noise
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)  # Increased timeout
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return None
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Please try again.")
            return None
        except sr.RequestError:
            speak("Sorry, I couldn't connect to the speech recognition service.")
            return None

# Function to get AI-generated responses (cleaned)
def generate_ai_response(user_input):
    try:
        response = model.generate_content(user_input)  # Fetch AI response
        ai_text = response.text if response else "I'm here to help."
        
        # Remove asterisks (*) and extra whitespace
        clean_text = re.sub(r"\*", "", ai_text).strip()

        return clean_text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Function to listen for "hello"
def listen_for_hello():
    speak("Listening for hello...")
    while True:
        text = listen()
        if text and "hello" in text:
            speak("Hello, I'm Neo, the assistant. Starting to detect your emotion.")
            return True

# Function to detect emotions for 30 seconds
def detect_emotions():
    cap = cv2.VideoCapture(0)
    start_time = time.time()

    emotion_counts = {
        "happy": 0, "sad": 0, "angry": 0, "surprised": 0,
        "neutral": 0, "fear": 0, "disgust": 0
    }
    total_frames = 0

    while (time.time() - start_time) < 30:  # Run for 30 seconds
        ret, frame = cap.read()
        if not ret:
            break

        emotions = detector.detect_emotions(frame)
        for emotion in emotions:
            (x, y, w, h) = emotion["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            dominant_emotion = max(emotion["emotions"], key=emotion["emotions"].get)
            cv2.putText(frame, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if dominant_emotion in emotion_counts:
                emotion_counts[dominant_emotion] += 1

        total_frames += 1
        cv2.imshow("Emotion Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Find the most detected emotion
    dominant_emotion = max(emotion_counts, key=emotion_counts.get)

    # Generate a response based on detected emotions
    if emotion_counts[dominant_emotion] >= total_frames / 2:
        if dominant_emotion == "sad":
            response = "I noticed you're feeling sad. Would you like to talk about it? Or maybe I can help you contact someone for support."
        elif dominant_emotion == "happy":
            response = "You seem happy! What's making you feel this way?"
        elif dominant_emotion == "angry":
            response = "I sense some frustration. Would you like me to suggest some ways to calm down?"
        elif dominant_emotion == "surprised":
            response = "You seem surprised! What happened?"
        elif dominant_emotion == "neutral":
            response = "You seem neutral. How can I assist you today?"
        elif dominant_emotion == "fear":
            response = "You seem scared. Is everything okay? I'm here to help."
        elif dominant_emotion == "disgust":
            response = "I noticed some discomfort. Do you want to talk about it?"

    else:
        response = "I'm here if you need to talk."

    speak(response)
    return response

# Function to handle the assistant conversation
def assistant_conversation():
    speak("You can now talk to me. Say 'exit' anytime to stop.")
    while True:
        user_input = listen()
        if user_input:
            if "exit" in user_input:
                speak("Goodbye! Take care.")
                break
            ai_response = generate_ai_response(user_input)
            speak(ai_response)

# Main execution
if listen_for_hello():
    detect_emotions()
    assistant_conversation()
