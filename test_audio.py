
import speech_recognition as sr
from pydub import AudioSegment

# Convertir l'audio en format WAV
audio = AudioSegment.from_file("WhatsApp Audio 2025-05-07 at 10.39.21.mp4")
audio.export("converted_audio.wav", format="wav")

# Reconnaissance vocale
recognizer = sr.Recognizer()
with sr.AudioFile("converted_audio.wav") as source:
    audio_data = recognizer.record(source)

text = recognizer.recognize_google(audio_data, language="fr-FR")
print(text)
