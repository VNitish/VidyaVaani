import os
import yt_dlp
from faster_whisper import WhisperModel
from transformers import pipeline
from googletrans import Translator

def extract_audio(url, output_path="audio.wav"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def transcribe_audio(audio_path):
    model = WhisperModel("base", compute_type="float32")  # use "medium" or "large-v2" for better accuracy
    segments, _ = model.transcribe(audio_path)

    transcript = ""
    for segment in segments:
        transcript += segment.text.strip() + " "

    return transcript.strip()

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize(text):
    return summarizer(text, max_length=150, min_length=40, do_sample=False)[0]['summary_text']

def translate_text(text, dest_lang="hi"):
    """
    Translates a block of text to the desired language using Google Translate.
    """
    translator = Translator()
    translated = translator.translate(text, dest=dest_lang)
    return translated.text

def main(youtube_url):
    # Step 1: Download Audio
    print("🔹 Extracting audio from YouTube...")
    extract_audio(youtube_url, output_path="audio.wav")

    # Step 2: Transcribe Audio using Faster-Whisper
    print("🔹 Transcribing audio...")
    transcript = transcribe_audio("audio.wav")

    # Step 3: Summarize Transcript
    print("🔹 Summarizing translated text...")
    summary = summarize(transcript)

    # Step 4: Translate summary
    print("🔹 Translating transcript...")
    translated_text = translate_text(summary)

    # Step 5: Output Result
    print("\n✅ Final Summary (Translated):\n")
    print(translated_text)

    return translated_text


