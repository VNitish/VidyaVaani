import os
from functions import tts_with_parler_segments
from functions import generate_ass
from functions import replace_audio_ffmpeg
from functions import video_to_translated_transcript
from functions import slow_down_video
from functions import get_speaker_name, download_video, extract_audio, transcribe_audio, translate_text

def process_video(video_url, language, voice):
    # Define the paths to check for the files
    video_path = "video.mp4"
    final_video_path = "final_output_video.mp4"
    final_audio_path = "final_hindi_audio.wav"
    subtitles_path = "subtitles.ass"
    final_translated_video_path = "final_translated_video.mp4"

    # Check and replace files if they already exist
    def check_and_replace(file_path):
        if os.path.exists(file_path):
            print(f" {file_path} already exists. Replacing the file.")
        else:
            print(f" {file_path} does not exist. Proceeding to create it.")

    # Step 1: Translate transcript
    print("Translating the video transcript...")
    translated_transcript = video_to_translated_transcript(video_url, language)

    # Step 2: Text-to-speech (TTS)
    check_and_replace(final_audio_path)
    print("🔊 Converting translated transcript to speech...")
    tts_with_parler_segments(translated_transcript, voice_description = get_speaker_name(language, voice))
    print("----------------------TEXT TO SPEECH DONE-----------------------------------")

    # Step 3: Generate subtitles
    check_and_replace(subtitles_path)
    print("📝 Generating subtitles...")
    generate_ass(translated_transcript)
    print("----------------------SUBTITLES GENERATED SUCCESSFULLY----------------------")

    # Step 4: Replace audio in the original video
    check_and_replace(final_video_path)
    print("Replacing video audio...")
    replace_audio_ffmpeg(video_path, final_audio_path)
    print("-----------------------VIDEO GENERATED SUCCESSFULLY-------------------------")

    # Step 5: Slow down the video
    # check_and_replace(final_translated_video_path)
    # print("⏳ Slowing down the video...")
    # slow_down_video(final_video_path, final_translated_video_path, slowdown_factor=1.2)
    # print("Final translated video generated successfully!")