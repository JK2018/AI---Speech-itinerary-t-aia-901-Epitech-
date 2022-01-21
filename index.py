from flask import Flask, render_template, redirect, request
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
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            print("filename : "+file.filename)
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)
            with audioFile as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                data = recognizer.record(source)
            transcript = recognizer.recognize_google(data, language='fr-FR', key=None)

    return render_template('home.html', transcript=transcript)

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

        print("res : "+transcript)

    return render_template('home.html', transcript=transcript)
   
@app.route("/result",methods=["GET", "POST"])
def result():
    userText = "Initialization"
    userText = request.form["textarea"].strip()
    cities = process_input(userText)
    # print("data : "+result)
    return render_template('home.html', transcript=cities)
