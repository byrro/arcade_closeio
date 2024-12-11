from arcade_closeio.tools.constants import BASE_URL


def get_url(endpoint: str) -> str:
    return f"{BASE_URL}/{endpoint.lstrip('/')}"


def get_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "ArcadeAI 'arcade-ai.com'",
    }
