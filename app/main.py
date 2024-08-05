from fastapi import FastAPI, Form, HTTPException
from typing import Optional
from urllib.parse import urlparse, urlunparse
from .utils import fetch_html_content, check_labels
from .models import URLRequest
from collections import Counter

app = FastAPI()

def ensure_url_scheme(url: str) -> str:
    """Ensure http:// is prefixed to the string"""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return urlunparse(parsed_url._replace(scheme='http'))
    return url

@app.post("/check")
async def check(url: Optional[str] = Form(None)):
    if url:
        url = ensure_url_scheme(url)
    
    url_request = URLRequest(url=url)

    if url_request.url:
        html_content = fetch_html_content(url_request.url)
        if html_content is None:
            raise HTTPException(status_code=400, detail="Failed to fetch HTML content from the provided URL.")
    else:
        raise HTTPException(status_code=400, detail="A URL must be provided.")

    # report = check_labels(html_content)
    # return {"report": report}
    report, error_summary = check_labels(html_content)
    return {"report": report, "error_summary": error_summary}
