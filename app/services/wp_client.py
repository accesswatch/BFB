import httpx
from typing import Optional


class WPClient:
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password) if username and password else None
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def publish_form(self, form_json: dict) -> httpx.Response:
        """Publish a form to Gravity Forms v2 endpoint. Caller handles auth and errors."""
        url = f"{self.base_url}/wp-json/gf/v2/forms"
        resp = self.client.post(url, json=form_json, auth=self.auth)
        resp.raise_for_status()
        return resp
