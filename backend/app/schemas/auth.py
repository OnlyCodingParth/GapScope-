from pydantic import BaseModel, Field


class GoogleCredential(BaseModel):
    credential: str = Field(min_length=1)
