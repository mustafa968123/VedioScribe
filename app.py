from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for serving the index page
@app.route('/')
def index():
    return render_template('open.html')

# Route for serving click.html page
@app.route('/click.html')
def click():
    return render_template('click.html')

# Route for serving main.html page
@app.route('/main.html')
def main():
    return render_template('main.html')

# Route for serving home.html page
@app.route('/home.html')
def home():
    return render_template('home.html')

# Route for serving static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)
# Route for handling audio-to-text conversion
@app.route('/convert_audio_to_text', methods=['POST'])
def convert_audio_to_text():
    try:
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Convert video to audio
            video_clip = VideoFileClip(file_path)
            audio_clip = video_clip.audio
            output_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.mp3')
            audio_clip.write_audiofile(output_audio_path)
            video_clip.close()
            audio_clip.close()

            # Convert audio to text
            sound = AudioSegment.from_mp3(output_audio_path)
            sound.export(os.path.join(app.config['UPLOAD_FOLDER'], 'transcript.wav'), format="wav")

            AUDIO_FILE = os.path.join(app.config['UPLOAD_FOLDER'], 'transcript.wav')

            r = sr.Recognizer()
            languages = ["hi-IN", "en-IN"]  

            transcriptions = {}  

            for language in languages:
                with sr.AudioFile(AUDIO_FILE) as source:
                    audio = r.record(source)
                    
                    try:
                        transcription = r.recognize_google(audio, language=language)
                        transcriptions[language] = transcription
                        print("Transcription ({0}): {1}".format(language, transcription))
                    except sr.UnknownValueError:
                        print("Speech recognition could not understand audio for language", language)
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service for language", language, "; {0}".format(e))
                
            # Write transcriptions to a text file
            transcript_text = ""
            for language, transcription in transcriptions.items():
                transcript_text += "Transcription ({0}): {1}\n".format(language, transcription)
            
            return render_template('result.html', transcript=transcript_text)

        else:
            return "Invalid file format. Please upload an MP4 file."
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
