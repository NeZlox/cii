from typing import List
from pydantic import BaseModel


class TagSchema(BaseModel):
    id: int
    name: str


class PicturesWithTagsSchema(BaseModel):
    id: int
    resolution_width: int
    resolution_height: int
    url_page: str
    url_image: str
    path: str
    tags: List[TagSchema]

    class Config:
        orm_mode = True


class ResponsePictures(BaseModel):
    data: List[PicturesWithTagsSchema]
