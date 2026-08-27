from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.services.groq_tts import GroqTTS


router = APIRouter()


# ==================================================
# LOAD TTS ONCE
# ==================================================

tts = GroqTTS(
    voice="hannah"
)


class TTSRequest(BaseModel):

    text: str


# ==================================================
# TTS ENDPOINT
# ==================================================

@router.post("/tts")
async def text_to_speech(
    request: TTSRequest
):

    if not request.text.strip():

        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    try:

        print()
        print(
            "=========================================="
        )

        print(
            "TTS REQUEST RECEIVED"
        )

        print(
            f"Text length: "
            f"{len(request.text)} characters"
        )

        print(
            "=========================================="
        )

        # ------------------------------------------
        # STREAM PCM CHUNKS
        # ------------------------------------------

        def audio_stream():

            try:

                for pcm in tts.generate_chunks(
                    request.text
                ):

                    print(
                        f"HTTP → Sending PCM chunk: "
                        f"{len(pcm)} bytes"
                    )

                    # ----------------------------------
                    # SEND CHUNK IMMEDIATELY
                    # ----------------------------------

                    yield pcm

            except Exception as e:

                print()
                print(
                    "TTS STREAM ERROR:"
                )

                print(
                    f"{type(e).__name__}: {e}"
                )

                # We don't raise HTTPException here
                # because the HTTP response has already
                # started streaming.

        return StreamingResponse(
            audio_stream(),
            media_type="audio/pcm",

            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:

        print()
        print(
            "TTS ENDPOINT ERROR:"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="TTS generation failed"
        )