from pydantic import BaseModel, Field
from typing import Optional

class CityExtraction(BaseModel):
    city_name: str = Field(description="city name")
    confidence: float = Field(ge=0.0, le=1.0, description="confidence score bw 0-1 for a city mentioned")
    date_reference:Optional[str] = Field(
        default=None,
        description="any date/time reference mentioned in the user query"
    )
    original_city_mention:Optional[str] = Field(default=None, description="original text that mentioned the city")