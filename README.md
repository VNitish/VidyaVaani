# VidyaVaani

## Educational video translation service

A web application that allows users to submit educational youTube video URLs for translation and transcription, powered by Flask, MongoDB, and Docker.

---

## Features

- **Submit educational youTube video URLs** for translation and transcription.
- **Select target language and voice** for translation.
- **Store translation requests in MongoDB**.
- **Text to speech is generated using Indic-Parler TTS**.
- **Transcription is done using OpenAI whisper, translated using google translate and then chunking is done before TTS**.
- **Customization regarding audio speed and chunk joining is done for sync**
- **Email notifications** (optional) for status updates.
- **Docker and Docker Compose** for easy setup and deployment.

---

## Quick Start

### 1. Clone the Repository


### 2. Build and Run with Docker Compose


- **Flask app:** available at [http://localhost:10000](http://localhost:10000)
- **MongoDB:** accessible internally and on port `27017` (if mapped)

### 3. (Optional) Run in Detached Mode


### 4. Stop the Services


---

> **Note:** Do not commit `.env` to version control.

---

## Troubleshooting

- **MongoDB connection issues:** Ensure MongoDB is running and the connection string is correct.
- **Email sending errors:** Verify your email credentials and use an App Password if using Gmail with 2FA.
- **Port conflicts:** Adjust the port mapping in `docker-compose.yml` if needed.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---



## Project Structure
```bash
yourrepo/
├── app.py/ # Flask application code
│ ├── templates/ # HTML templates
├── Dockerfile # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt # Python dependencies
├── .gitignore
├── functions.py
├── translation.py
├── summarizer.py
├── send_email.py
└── README.md # This file

----

## Contact

For questions or support, please contact nitish2002.nn@gmail.com.


