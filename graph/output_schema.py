from pydantic import BaseModel, Field

class TravelOutput(BaseModel):
    city_summary: str = Field(..., description= "Final city summary on rendered ui")
    weather_forecast: list[str] = Field(default_factory=list, description= "weather forecast for display")
    image_urls: list[str] = Field(default_factory=list, description= "image urls rendered on ui")