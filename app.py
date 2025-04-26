from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from translation import process_video
from send_email import send_email_with_attachments

# Initialize app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/translate', methods=['POST'])
def translate_video():
    data = request.get_json()
    video_url = data['url']
    language = data['language']
    voice = data['voice']
    email = data['email']

    logger.info(f"Received request: url={video_url}, language={language}, voice={voice}, email={email}")

    try:
        logger.info("Starting video processing...")
        translated_transcript = process_video(video_url, language, voice)
        logger.info("Video processing completed.")

        video_file_path = "final_output_video.mp4"
        subtitles_file_path = "subtitles.ass"

        subject = "Your Translated Video and Subtitles"
        body = "Hi, your translated video and subtitles are ready. Please find them attached."

        logger.info("Sending email with attachments...")
        send_email_with_attachments(email, subject, body, video_file_path, subtitles_file_path)
        logger.info("Email sent successfully.")

        return jsonify({"success": True, "message": "Translation and email sent!"})

    except Exception as e:
        logger.error(f"Error during translation or email sending: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
