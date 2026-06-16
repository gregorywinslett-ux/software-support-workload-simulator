from __future__ import annotations

from io import BytesIO
from urllib.parse import urlencode

import qrcode


def participant_url(base_url: str, activity: str) -> str:
    cleaned = base_url.rstrip("/") or "http://localhost:8501"
    return f"{cleaned}/?{urlencode({'role': 'participant', 'activity': activity})}"


def qr_png_bytes(url: str) -> bytes:
    image = qrcode.make(url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
