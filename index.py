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

        if "file" not in request.files:
            return json.dumps({"error": "Aucun fichier n'a été envoyé."})

        file = request.files["file"]
        if file.filename == "":
            return json.dumps({"error": "Le fichier envoyé est invalide."})

        if not file.filename.endswith(('.wav', '.aif', '.aiff', '.flac')):
            return json.dumps({"error": "Le fichier audio doit être au format .wav, .aif, .aiff ou .flac."})

        if file:
            print("filename : "+file.filename)
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)
            with audioFile as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                data = recognizer.record(source)
            transcript = recognizer.recognize_google(data, language='fr-FR', key=None)

        spam_filter_status = request.args["spam_filter"] == "true" if "spam_filter" in request.args else False

        return process_render(transcript, spam_filter_status)


@app.route("/sttMic",methods=["GET", "POST"])
def sttMic():

    transcript = ""
    print(request.get_json())
    if request.method == "POST":
        print("Mic transalation request")

        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("We are listen you can speak")
            recognizer.adjust_for_ambient_noise(source, duration=0.5) 
            audio = recognizer.listen(source)
        transcript = recognizer.recognize_google(audio, language='fr-FR', key=None)

        spam_filter_status = request.args["spam_filter"] == "true" if "spam_filter" in request.args else False

        print("res : "+transcript.strip())
        return process_render(transcript, spam_filter_status)


@app.route("/result",methods=["GET", "POST"])
def result():
    userText = "Initialization"
    userText = request.form["doc"].strip()
    spam_filter_status = request.args["spam_filter"] == "true" if "spam_filter" in request.args else False
    return process_render(userText, spam_filter_status)


def process_render(doc, spam_filter_status):
    if (doc == "" or (spam_filter_status and process_spam_filter(doc))):
        return json.dumps({"error": "La recherche n'est pas valide."})

    cities = process_input(doc)
    if not cities:
        return json.dumps({"error": "Aucun itinéraire n'a été trouvé."})

    route = process_path_finding(cities[0], cities[1])
    return json.dumps(route)