import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

load_dotenv()

app = FastAPI()


# Allow your frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://portfolio-flax-one-6vxiqbbagt.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


@app.get("/")
def root():
    return {"message": "Contact API is running"}


@app.post("/contact")
def send_contact_email(form: ContactForm):

    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        raise HTTPException(
            status_code=500,
            detail="Email configuration is missing"
        )

    email = EmailMessage()

    email["From"] = sender_email
    email["To"] = sender_email
    email["Reply-To"] = form.email
    email["Subject"] = f"Portfolio Contact: {form.subject}"

    email.set_content(
        f"""
            New message from your portfolio

            Name: {form.name}
            Email: {form.email}
            Subject: {form.subject}

            Message:
            {form.message}
        """
    )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, app_password)
            smtp.send_message(email)

        return {
            "success": True,
            "message": "Message sent successfully"
        }

    except Exception as e:
        print("Email error:", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to send email"
        )