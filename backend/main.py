import os

import resend
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

load_dotenv()

app = FastAPI()

# Allow your Vercel frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://portfolio-flax-one-6vxiqbbagt.vercel.app"
    ],
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

    resend_api_key = os.getenv("RESEND_API_KEY")

    if not resend_api_key:
        raise HTTPException(
            status_code=500,
            detail="Resend API key is missing"
        )

    resend.api_key = resend_api_key

    try:
        params = {
            "from": "Portfolio <onboarding@resend.dev>",
            "to": ["vanshulthakur007@gmail.com"],
            "subject": f"Portfolio Contact: {form.subject}",
            "html": f"""
                <h2>New message from your portfolio</h2>

                <p><strong>Name:</strong> {form.name}</p>

                <p><strong>Email:</strong>
                {form.email}</p>

                <p><strong>Subject:</strong>
                {form.subject}</p>

                <h3>Message</h3>

                <p>{form.message}</p>

                <hr>

                <p>
                    You can reply directly to:
                    <strong>{form.email}</strong>
                </p>
            """
        }

        email = resend.Emails.send(params)

        print("Email sent:", email)

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