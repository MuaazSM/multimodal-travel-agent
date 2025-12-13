from typing import Optional, Literal
from pydantic import BaseModel, Field

class TravelState(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    user_query: str = ""
    city: Optional[str] = None
    previous_city: Optional[str] = None
    date_range: Optional[str] = None
    route: Optional[Literal["vector", "web"]] = None
    city_summary: Optional[str] = None
    weather_forecast: list[dict] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    conversation_history: list[dict] = Field(default_factory=list)
    skip_summary: bool = False
    skip_images: bool = False