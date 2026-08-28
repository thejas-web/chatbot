import os

from groq import Groq
from backend.config import groq_api_key


class GroqSTT:

    def __init__(self):

        print("Initializing Groq Whisper STT...")

        if not groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set"
            )

        self.client = Groq(
            api_key=groq_api_key
        )

        print("Groq Whisper STT initialized.")

    def transcribe(self, audio_path: str) -> str:

        print("Sending audio to Groq Whisper...")

        with open(audio_path, "rb") as audio_file:

            transcription = (
                self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    language="en",
                    prompt=(
                        "Webenza is spelled "
                        "W-E-B-E-N-Z-A. "
                        "Webenza is a company. "
                        "Webenza services and "
                        "Webenza website."
                    ),
                    response_format="json",
                    temperature=0
                )
            )

        text = transcription.text.strip()

        print(
            "Groq Whisper transcript:",
            text
        )

        return text