from pydantic import BaseModel, HttpUrl, validator
from typing import Optional

class URLRequest(BaseModel):
    url: Optional[HttpUrl] = None

    @validator("url", pre=True, always=True)
    def validate_and_correct_url(cls, value):
        if value and not str(value).startswith(('http://', 'https://')):
            value = 'http://' + str(value)
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "url": "http://example.com"
            }
        }
