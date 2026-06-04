from pydantic import BaseModel, Field


class MoodEntry(BaseModel):
    day: str = Field(..., description="Day initial, e.g., 'L', 'M', 'M'")
    level: float = Field(..., description="Mood level between 0.0 and 1.0")
    label: str = Field(
        ...,
        description="Mood label, e.g., 'Alegría', 'Nostalgia', or 'Sin registro'",
    )


class TopicEntry(BaseModel):
    name: str = Field(..., description="Topic name")
    percentage: int = Field(..., description="Percentage of this topic in the week")


class WellnessResponse(BaseModel):
    week: str = Field(..., description="Formatted string of the current week")
    moods: list[MoodEntry] = Field(..., description="List of 7 mood entries for the week")
    topics: list[TopicEntry] = Field(..., description="List of top topics with their percentages")
