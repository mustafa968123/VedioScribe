from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment

# Path to the video file
video_path = "C:\Users\musta\OneDrive\Desktop\Minor 2\static\uploads\Advanced_English_Vocabulary_shorts.mp4"

# Extract audio from the video
video_clip = VideoFileClip(video_path)
audio_clip = video_clip.audio
output_audio_path = "opaudio.mp3"
audio_clip.write_audiofile(output_audio_path)

# Close video and audio clips
video_clip.close()
audio_clip.close()

# Convert MP3 to WAV for transcription
sound = AudioSegment.from_mp3(output_audio_path)
transcript_audio_path = "transcript.wav"
sound.export(transcript_audio_path, format="wav")

# Transcribe audio
AUDIO_FILE = transcript_audio_path
r = sr.Recognizer()
languages = ["hi-IN", "en-IN"]

for language in languages:
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)

        try:
            transcription = r.recognize_google(audio, language=language)
            print("Transcription ({0}): {1}".format(language, transcription))
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio for language", language)
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service for language", language, "; {0}".format(e))
