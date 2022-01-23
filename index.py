import json 
from flask import Flask, render_template, request
import speech_recognition as sr
from nlp_service import process_input

# Init Flask App
app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template('home.html')


@app.route("/sttFile",methods=["GET", "POST"])
def sttFile():
    transcript = ""
    if request.method == "POST":
        print("File transalation request")

        if "file" not in request.files:
            return render_template('home.html', error="Aucun fichier n'a été envoyé.")

        file = request.files["file"]
        if file.filename == "":
            return render_template('home.html', error="Le fichier envoyé est invalide.")

        if not file.filename.endswith(('.wav', '.aif', '.aiff', '.flac')):
            return render_template('home.html', error="Le fichier audio doit être au format .wav, .aif, .aiff ou .flac.")

        if file:
            print("filename : "+file.filename)
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)
            with audioFile as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                data = recognizer.record(source)
            transcript = recognizer.recognize_google(data, language='fr-FR', key=None)

        return process_render(transcript)


@app.route("/sttMic",methods=["GET", "POST"])
def sttMic():

    transcript = ""
    if request.method == "POST":
        print("Mic transalation request")

        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("We are listen you can speak")
            recognizer.adjust_for_ambient_noise(source, duration=0.5) 
            audio = recognizer.listen(source)
        transcript = recognizer.recognize_google(audio, language='fr-FR', key=None)  

        print("res : "+transcript.strip())
        return process_render(transcript)


@app.route("/result",methods=["GET", "POST"])
def result():
    userText = "Initialization"
    userText = request.form["doc"].strip()
    return process_render(userText)


def process_render(doc):
    # cities = process_input(doc)
    route = [
        {'city': 'Toulouse', 'station': 'Gare de Toulouse Matabiau', 'lat': 43.61146412, 'lng': 1.45355763},
        {'city': 'Bordeaux', 'station': 'Gare de Bordeaux-St-Jean', 'lat': 44.82653979, 'lng': -0.55619406},
        {'city': 'Nantes', 'station': 'Gare de Nantes', 'lat': 47.21750472, 'lng': -1.54192517},
        {'city': 'Paris', 'station': 'Gare de Paris-Montparnasse', 'lat': 48.84062983, 'lng': 2.31989439},
    ]
    return render_template('home.html', transcript=json.dumps(route))