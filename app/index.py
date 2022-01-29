import simplejson as json
from flask import Flask, render_template, request
import speech_recognition as sr
from nlp_service import process_input
from path_finding import process_path_finding
from spam_filter import process_spam_filter

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
        print(request)
        print(request.files)

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
    if (process_spam_filter(doc)):
        return {"error": "La recherche n'est pas valide."}

    cities = process_input(doc)
    route = process_path_finding(cities[0], cities[1])

    return json.dumps(route)