'''Importing all the necessary libraries'''
import os
import time  
import shlex
import torch
import math
import re
import whisper
import tempfile
import subprocess
import numpy as np
from tqdm import tqdm
from pydub import AudioSegment
from pydub.effects import speedup
from googletrans import Translator
from scipy.io.wavfile import write as write_wav
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
from moviepy import VideoFileClip, AudioFileClip, vfx

# OUT_LANG = "hi"
# GENDER = "male"

def get_speaker_name(language, gender):
    """
    Returns a recommended speaker name based on language and gender.
    Only supports Hindi, Marathi, Bengali.
    """
    recommended_speakers = {
        "hindi": {
            "male": ["Rohit"],
            "female": ["Divya"]
        },
        "mr": {
            "male": ["Sanjay"],
            "female": ["Sunita"]
        },
        "bengali": {
            "male": ["Arjun"],
            "female": ["Aditi"]
        },
    }

    language = language.lower()
    gender = gender.lower()

    if language not in recommended_speakers:
        raise ValueError("Unsupported language. Choose from Hindi, Marathi, Bengali.")
    
    if gender not in recommended_speakers[language]:
        raise ValueError(f"{gender.capitalize()} speaker not available for {language.capitalize()}.")

    return recommended_speakers[language][gender][0] + "speaks at a extremely fast pace with a slightly moderate-pitched voice, captured clearly in a close-sounding environment with excellent recording quality"

def download_video(url, output_path="video.mp4"):
    """
    Downloads the video using yt-dlp.
    """
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "-o", output_path,
        url
    ]
    subprocess.run(cmd, check=True)
    return output_path

def extract_audio(video_path, audio_output_path="audio.mp3"):
    """
    Extracts audio from video and saves as MP3.
    """
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_output_path)

def transcribe_audio(audio_path, model_size="base"):
    """
    Uses OpenAI Whisper to transcribe audio and returns segments with timestamps.
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["segments"]  # This contains timestamps + text

def translate_text(text, dest_lang):
    """
    Translates a block of text to the desired language using Google Translate.
    """
    translator = Translator()
    translated = translator.translate(text, dest=dest_lang)
    return translated.text

def video_to_translated_transcript(video_url, dest_lang):
    """
    Full process from video URL to translated transcript with timestamps.
    """
    # Save video to current directory
    video_path = "video.mp4"

    # Download video once, keep it
    print("[1] Downloading video...")
    download_video(video_url, video_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")

        print("[2] Extracting audio...")
        extract_audio(video_path, audio_path)

        print("[3] Transcribing...")
        segments = transcribe_audio(audio_path)

        print("[4] Translating each segment...")
        translated_segments = []
        for segment in segments:
            translated_text = translate_text(segment["text"], dest_lang = dest_lang)
            translated_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "original_text": segment["text"],
                "translated_text": translated_text
            })

    return translated_segments

def tts_with_parler_segments(segments, output_path="final_hindi_audio.wav",
                              voice_description = "Rohit speaking extremely fast"):
    """
    Generate speech using Indic-Parler-TTS model.
    All segments are sped up 1.3x and played sequentially — no truncation of audio.
    """

    def speed_up_audio(audio_segment, speed=1.3):
        return speedup(audio_segment, playback_speed=speed, chunk_size=50, crossfade=10)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts").to(device)
    tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
    description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

    sample_rate = model.config.sampling_rate
    full_audio = AudioSegment.silent(duration=0)

    print("🔊 Generating audio sequentially using Indic-Parler-TTS...\n")

    for idx, seg in enumerate(tqdm(segments, desc="🔄 Generating segments")):
        prompt = seg["translated_text"]

        # Tokenize prompt and description
        description_input_ids = description_tokenizer(voice_description, return_tensors="pt").to(device)
        prompt_input_ids = tokenizer(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            generation = model.generate(
                input_ids=description_input_ids.input_ids,
                attention_mask=description_input_ids.attention_mask,
                prompt_input_ids=prompt_input_ids.input_ids,
                prompt_attention_mask=prompt_input_ids.attention_mask
            )

        audio_arr = generation.cpu().numpy().squeeze()
        segment_audio = AudioSegment(
            (audio_arr * 32767).astype(np.int16).tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )

        # Speed up by 1.3x
        segment_audio = speed_up_audio(segment_audio, speed=1.3)

        # Optional: Add small silence padding between sentences
        segment_audio += AudioSegment.silent(duration=200)  # 200ms silence

        full_audio += segment_audio

    full_audio = full_audio.set_frame_rate(sample_rate)
    full_audio.export(output_path, format="wav")
    print(f"\n✅ Continuous Indic-Parler-TTS audio saved to: {output_path}")

def slow_down_video(input_video_path, output_video_path, slowdown_factor=1.1):
    """
    Slows down the playback speed of a video by the given slowdown_factor.
    
    Args:
        input_video_path (str): Path to the input video file.
        output_video_path (str): Path where the slowed-down video will be saved.
        slowdown_factor (float): Factor by which to slow down (e.g., 1.2 = 20% slower).
    """
    print(f"🔵 Loading video: {input_video_path} ...")
    clip = VideoFileClip(input_video_path)

    # Apply slow-down effect
    slowed_clip = clip.fx(vfx.speedx, factor=(1/slowdown_factor))

    print(f"🛠️ Slowing down by {slowdown_factor}x...")
    slowed_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

    print(f"✅ Slowed down video saved to: {output_video_path}")

def generate_ass(segments, ass_path="subtitles.ass"):
    """Generate Advanced SubStation Alpha subtitles with black background"""
    
    def format_time(seconds):
        """Convert seconds to SRT/ASS time format (HH:MM:SS.SSS)"""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02}:{mins:02}:{secs:02}.{millis:03}"

    style = (
        "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H80000000,&H80000000,"
        "-1,0,0,0,100,100,0,0,1,3,3,2,10,10,10,1"
    )
    
    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write("[Script Info]\n")
        f.write("ScriptType: v4.00+\n\n")
        f.write("[V4+ Styles]\n")
        f.write(f"{style}\n\n")
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Text\n")
        
        for seg in segments:
            start = format_time(seg['start']).replace(",", ".")  # Now works
            end = format_time(seg['end']).replace(",", ".")
            text = seg['translated_text'].strip().replace("\n", "\\N")
            f.write(f"Dialogue: 0,{start},{end},Default,{text}\n")
    
    print(f"✅ ASS subtitle with black background created at {ass_path}")

def replace_audio_ffmpeg(original_video, tts_audio, final_output="final_output_video.mp4"):
    """
    Replace the original audio in the video with the provided TTS audio using ffmpeg.
    Ensures proper .mp4 output playable everywhere.
    """
    try:
        print("🔊 Replacing audio with TTS output...")
        
        merge_cmd = [
            "ffmpeg", "-y",
            "-i", original_video,
            "-i", tts_audio,
            "-c:v", "copy",               # Copy video stream without re-encoding
            "-c:a", "aac",                 # Re-encode audio to AAC (for mp4 compatibility)
            "-strict", "experimental",     # For AAC codec if needed
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-movflags", "+faststart",      # Important for .mp4 proper structure
            final_output
        ]
        
        subprocess.run(merge_cmd, check=True)
        print(f"🎉 Final video created at: {final_output}")

    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg error:", e)



