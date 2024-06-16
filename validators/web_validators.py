from fastapi import HTTPException, Response, status
import httpx
from common import google_verify_url, config

async def verify_captcha_completed(captcha_response: str) -> bool:
    """
    Verify that the captcha was completed.

    Args:
        captcha_response (str): The response from the captcha.

    Returns:
        bool: True if the captcha was completed, False otherwise.
    """
    url: str = google_verify_url + captcha_response
    try:
        async with httpx.AsyncClient() as client:
            captcha_request: Response = await client.get(url)
            captcha_request.raise_for_status()
            if captcha_response.json()["success"]: return True
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to verify captcha response.")
    return False