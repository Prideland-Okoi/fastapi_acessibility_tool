from fastapi import FastAPI, HTTPException
from .models import URLRequest
from .utils import fetch_html_content, check_labels

app = FastAPI()

@app.post("/check")
async def check(url_request: URLRequest):
    html_content = fetch_html_content(url_request.url)
    if html_content is None:
        raise HTTPException(status_code=400, detail="Failed to fetch HTML content from the provided URL.")
    
    report = check_labels(html_content)
    return report
