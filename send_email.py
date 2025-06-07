import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email_with_attachments(to_email, subject, body, video_file_path, subtitles_file_path):
    # Sender email credentials (Make sure you use app-specific password if using Gmail)
    sender_email = "nitishnaidu.iitb@gmail.com"  # Replace with your email
    sender_password = "Focw@2002"  # Replace with your email app-specific password

    # Create the MIMEMultipart object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body of the email
    msg.attach(MIMEText(body, 'plain'))

    # Attach the video file
    attach_file(video_file_path, msg)
    # Attach the subtitles file
    attach_file(subtitles_file_path, msg)

    # Establish an SMTP connection
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use Gmail's SMTP server
        server.starttls()  # Encrypt the connection
        server.login(sender_email, sender_password)

        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

    finally:
        server.quit()

def attach_file(file_path, msg):
    """Attach the given file to the email message."""
    try:
        # Open the file to be sent
        with open(file_path, "rb") as attachment:
            # Create a MIMEBase object for the attachment
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(file_path)}")
            msg.attach(part)
    except Exception as e:
        print(f"Error attaching file {file_path}: {e}")


