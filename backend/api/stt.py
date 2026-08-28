
import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException

#from backend.services.whisper_stt import WhisperSTT
from backend.services.groq_stt import GroqSTT

router = APIRouter()


# Load Whisper once when this module is imported.
# We DON'T want to load the model for every request.
#whisper = WhisperSTT()


groq_stt = GroqSTT()

@router.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...)
):

    temp_path = None

    try:

        print(
            "Received audio:",
            audio.filename,
            audio.content_type
        )

        # Create temporary file
        suffix = ".webm"

        if audio.filename:
            _, extension = os.path.splitext(
                audio.filename
            )

            if extension:
                suffix = extension

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_path = temp_file.name

            audio_bytes = await audio.read()

            temp_file.write(audio_bytes)

        print(
            "Audio saved:",
            temp_path
        )

        # -----------------------------------------
        # WHISPER TRANSCRIPTION
        # -----------------------------------------

        text = groq_stt.transcribe(
            temp_path
        )

        if not text:

            return {
                "text": "",
                "message": "No speech detected."
            }

        return {
            "text": text
        }

    except Exception as e:

        print(
            "STT error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Speech transcription failed"
        )

    finally:

        # Delete temporary audio file
        if temp_path and os.path.exists(
            temp_path
        ):

            try:
                os.remove(temp_path)

            except Exception as e:

                print(
                    "Could not delete temp file:",
                    e
                )