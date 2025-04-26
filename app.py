from flask import Flask, request, jsonify
from flask_cors import CORS
from translation import process_video
from send_email import send_email_with_attachments


app = Flask(__name__)
CORS(app)

@app.route('/translate', methods=['POST'])
def translate_video():
    data = request.get_json()
    video_url = data['url']
    language = data['language']
    voice = data['voice']
    email = data['email']

    try:
        translated_transcript = process_video(video_url, language, voice)
        video_file_path = "final_output_video.mp4"
        subtitles_file_path = "subtitles.ass"
        subject = "Your Translated Video and Subtitles"
        body = "Hi, your translated video and subtitles are ready. Please find them attached."
        send_email_with_attachments(email, subject, body, video_file_path, subtitles_file_path)

        return jsonify({"success": True, "message": "Translation and email sent!"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
