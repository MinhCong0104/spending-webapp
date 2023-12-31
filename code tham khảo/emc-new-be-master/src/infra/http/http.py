import httpx
import json

from src.config.settings import settings

def get_http_client(*args, **kargs):
    return httpx.AsyncClient(*args, **kargs, timeout=settings.http_client_time_out)

def get_response_json(response: httpx.Response):
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        return None
 