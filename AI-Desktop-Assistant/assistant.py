import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import pygame
import math
import threading
import random
import time
import psutil
import requests
import traceback

# ================== RESPONSES ==================
ACK_RESPONSES = ["Got it.", "On it.", "Sure.", "Working on it.", "Okay."]
WAKE_RESPONSES = ["Yes Sohan", "I'm listening", "Go ahead", "Ready"]
SEARCH_RESPONSES = ["Searching now", "Give me a moment", "Looking it up"]

# ================== UI SETUP ==================
pygame.init()

WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jarvis AI")

clock = pygame.time.Clock()
state = "idle"
angle = 0

# ================== SPEECH ENGINE ==================
engine = pyttsx3.init()
voices = engine.getProperty('voices')

selected = False
for voice in voices:
    if "zira" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        selected = True
        break

if not selected:
    engine.setProperty('voice', voices[0].id)

engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# ================== LOAD IMAGES ==================
try:
    bg = pygame.image.load("face/bg.png")
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

    idle_img = pygame.image.load("face/idle.png")
    listening_img = pygame.image.load("face/listening.png")
    speaking_img = pygame.image.load("face/speaking.png")

    idle_img = pygame.transform.scale(idle_img, (300, 400))
    listening_img = pygame.transform.scale(listening_img, (300, 400))
    speaking_img = pygame.transform.scale(speaking_img, (300, 400))

except Exception as e:
    print("Image Loading Error:", e)
    input("Press Enter to exit...")
    exit()

# ================== SPEAK ==================
def speak(text):
    global state
    state = "speaking"
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()
    state = "idle"

# ================== LISTEN ==================
def listen():
    global state

    r = sr.Recognizer()
    r.energy_threshold = 180
    r.dynamic_energy_threshold = True
    r.pause_threshold = 1.2
    r.phrase_threshold = 0.3
    r.non_speaking_duration = 0.5

    with sr.Microphone() as source:
        state = "listening"
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            state = "idle"
            return ""

    try:
        command = r.recognize_google(audio, language="en-IN")
        state = "idle"
        print("You:", command)
        return command.lower()

    except sr.UnknownValueError:
        state = "idle"
        return ""

    except sr.RequestError:
        state = "idle"
        speak("Internet connection issue")
        return ""

# ================== WEATHER ==================
def get_weather():
    city = "Hyderabad"
    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url)
        data = response.json()

        current = data["current_condition"][0]
        temperature = current["temp_C"]
        feels_like = current["FeelsLikeC"]
        humidity = current["humidity"]
        weather = current["weatherDesc"][0]["value"]

        report = (
            f"The weather in {city} is {weather}. "
            f"Temperature is {temperature}°C. "
            f"It feels like {feels_like}°C. "
            f"Humidity is {humidity}%."
        )

        speak(report)

    except Exception as e:
        print("Weather Error:", e)
        speak("Sorry, I could not fetch weather updates.")

# ================== CONTACTS ==================
contacts = {
    "rohan": "918008269333",
    "me": "918008043111",
    "papa": "919110386473"
}

# ================== COMMANDS ==================
def process_command(command):
    try:
        # -------- SHUTDOWN --------
        if "shutdown" in command:
            speak("Say confirm shutdown or cancel")
            confirm = listen()

            if "confirm shutdown" in confirm:
                speak("Shutting down in 10 seconds")
                os.system("shutdown /s /t 10")
            else:
                speak("Shutdown cancelled")

        # -------- LOCK --------
        elif "lock" in command:
            speak("Locking system")
            os.system("rundll32.exe user32.dll,LockWorkStation")

        # -------- YOUTUBE --------
        elif "youtube" in command:
            speak(random.choice(ACK_RESPONSES))
            webbrowser.open_new_tab("https://www.youtube.com")

        # -------- WHATSAPP --------
        elif "whatsapp" in command:
            speak(random.choice(ACK_RESPONSES))
            path = r"C:\Users\sohan\OneDrive\Desktop\WhatsApp.lnk"

            if os.path.exists(path):
                os.startfile(path)
            else:
                speak("WhatsApp shortcut not found")

        # -------- GOOGLE --------
        elif "google" in command:
            speak(random.choice(ACK_RESPONSES))
            webbrowser.open("https://www.google.com")

        # -------- SPOTIFY --------
        elif "spotify" in command:
            speak(random.choice(ACK_RESPONSES))
            webbrowser.open("https://open.spotify.com")

        # -------- IDLE --------
        elif "idle" in command:
            speak(random.choice(ACK_RESPONSES))
            os.system("start python -m idlelib")

        # -------- TIME / DATE --------
        elif "time" in command or "date" in command or "day" in command:
            current_time = time.strftime("%I:%M %p")
            current_date = time.strftime("%B %d, %Y")
            current_day = time.strftime("%A")

            speak(f"It is {current_day}, {current_date}, {current_time}")

        # -------- BATTERY --------
        elif "battery" in command or "charging" in command:
            battery = psutil.sensors_battery()

            if battery:
                percent = battery.percent
                if battery.power_plugged:
                    speak(f"Battery is {percent} percent and charging")
                else:
                    speak(f"Battery is {percent} percent")
            else:
                speak("Battery info not available")

        # -------- WEATHER --------
        elif "weather" in command:
            speak("Checking weather")
            get_weather()

        # -------- VOLUME --------
        elif "volume up" in command:
            os.system("nircmd changesysvolume 5000")
            speak("Volume increased")

        elif "volume down" in command:
            os.system("nircmd changesysvolume -5000")
            speak("Volume decreased")

        # -------- CALL --------
        elif "call" in command:
            for name, number in contacts.items():
                if name in command:
                    speak(f"Calling {name}")
                    webbrowser.open(f"tel:{number}")
                    return
            speak("Contact not found")

        # -------- EXIT --------
        elif "exit" in command or "stop" in command:
            speak("Goodbye")
            pygame.quit()
            exit()

        # -------- DEFAULT SEARCH --------
        else:
            speak(random.choice(SEARCH_RESPONSES))
            webbrowser.open(
                f"https://www.google.com/search?q={command}"
            )

    except Exception as e:
        print("COMMAND ERROR:", e)
        traceback.print_exc()
        speak("An error occurred")

# ================== ASSISTANT LOOP ==================
def assistant_loop():
    print("Assistant Ready")
    active = False

    while True:
        try:
            command = listen()
            if not command:
                continue

            if "jarvis" in command:
                speak(random.choice(WAKE_RESPONSES))
                command = command.replace("jarvis", "").strip()
                active = True

                if command:
                    process_command(command)
                continue

            if active:
                process_command(command)

        except Exception:
            traceback.print_exc()

# ================== UI LOOP ==================
def ui_loop():
    global angle

    while True:
        screen.blit(bg, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        y_offset = int(math.sin(angle) * 5)
        angle += 0.05

        if state == "idle":
            screen.blit(idle_img, (100, 50 + y_offset))
        elif state == "listening":
            screen.blit(listening_img, (100, 50 + y_offset))
        elif state == "speaking":
            screen.blit(speaking_img, (100, 50 + y_offset))

        pygame.display.flip()
        clock.tick(60)

# ================== START ==================
if __name__ == "__main__":
    threading.Thread(target=assistant_loop, daemon=True).start()
    ui_loop()
