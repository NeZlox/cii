from typing import List

from pydantic import BaseModel


class PredictedTagsResponse(BaseModel):
    filename: str
    predicted_tags: List[str]
