from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import os
from translation import process_video
from send_email import send_email_with_attachments
# from summarizer import main as summarize_youtube_video  # Import the summarizer main function

from pymongo import MongoClient
from datetime import datetime


def create_app():
    app = Flask(__name__)
    
    # MongoDB configuration
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/vidyavaanitrial')
    client = MongoClient(mongo_uri)
    db = client.get_database()
    
    # Initialize collections
    app.db = db
    app.requests_collection = db.requests
    
    return app

# Initialize app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/vidyavaanitrial?directConnection=true")
db = mongo_client.get_database()  
requests_collection = db.requests

# Serve the frontend
@app.route('/')
def home():
    return render_template('index.html')  # Looks in templates/index.html

@app.route('/translate', methods=['POST'])
def translate_video():
    data = request.get_json()
    # Gather all fields from the request (add more as needed)
    video_url = data.get('url')
    language = data.get('language')
    voice = data.get('voice')
    email = data.get('email')
    school = data.get('school')
    district = data.get('district')
    state = data.get('state')
    requested_at = datetime.utcnow()

    logger.info(f"Received translation request: url={video_url}, language={language}, voice={voice}, email={email}, school={school}, district={district}, state={state}")

    # Insert request data into MongoDB
    try:
        request_doc = {
            "url": video_url,
            "language": language,
            "voice": voice,
            "email": email,
            "school": school,
            "district": district,
            "state": state,
            "requested_at": requested_at
        }
        requests_collection.insert_one(request_doc)
        logger.info("Request data inserted into MongoDB.")
    except Exception as db_exc:
        logger.error(f"Error inserting into MongoDB: {str(db_exc)}", exc_info=True)
        return jsonify({"success": False, "message": f"Database error: {str(db_exc)}"})

    # Continue with translation and email logic
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

# @app.route('/summarize', methods=['POST'])
# def summarize_video():
#     data = request.get_json()
#     video_url = data['url']

#     logger.info(f"Received summarization request: url={video_url}")

#     try:
#         logger.info("Starting summarization process...")
#         translated_summary = summarize_youtube_video(video_url)
#         logger.info("Summarization completed.")

#         return jsonify({"success": True, "translated_summary": translated_summary})

#     except Exception as e:
#         logger.error(f"Error during summarization: {str(e)}", exc_info=True)
#         return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
