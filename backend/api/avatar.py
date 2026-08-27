from fastapi import APIRouter, HTTPException
import httpx

from config import SIMLI_API_KEY, SIMLI_FACE_ID

router = APIRouter()

@router.get("/avatar-token")
async def get_avatar_token():

    if not SIMLI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="SIMLI_API_KEY is not configured"
        )

    if not SIMLI_FACE_ID:
        raise HTTPException(
            status_code=500,
            detail="SIMLI_FACE_ID is not configured"
        )

    payload = {
        "faceId": SIMLI_FACE_ID,
        "handleSilence": True,
        "maxSessionLength": 600,
        "maxIdleTime": 180,
    }

    headers = {
        "Content-Type": "application/json",
        "x-simli-api-key": SIMLI_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.simli.ai/compose/token",
            json=payload,
            headers=headers,
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )

    data = response.json()

    return {
        "session_token": data["session_token"],
        "face_id": SIMLI_FACE_ID,
    }
