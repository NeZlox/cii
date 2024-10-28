from typing import Optional

from pydantic import BaseModel, HttpUrl

__all__ = [
    'TagsSchema', 'TagsCreateSchema', 'TagsUpdateSchema',
    'PicturesSchema', 'PicturesCreateSchema', 'PicturesUpdateSchema',
    'PictureToTagsSchema', 'PictureToTagsCreateSchema', 'PictureToTagsUpdateSchema',
    'ModelSchema', 'ModelCreateSchema', 'ModelUpdateSchema'
]


class TagsSchema(BaseModel):
    id: int
    name: str


class TagsCreateSchema(BaseModel):
    name: str


class TagsUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None


class PicturesSchema(BaseModel):
    id: int
    resolution_width: int
    resolution_height: int
    url_page: HttpUrl
    url_image: HttpUrl
    path: str


class PicturesCreateSchema(BaseModel):
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    url_page: HttpUrl
    url_image: HttpUrl
    path: str


class PicturesUpdateSchema(BaseModel):
    id: int
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    url_page: Optional[HttpUrl] = None
    url_image: Optional[HttpUrl] = None
    path: Optional[str] = None


class PictureToTagsSchema(BaseModel):
    id_tag: int
    id_picture: int


class PictureToTagsCreateSchema(BaseModel):
    id_tag: int
    id_picture: int


class PictureToTagsUpdateSchema(BaseModel):
    pass


class ModelSchema(BaseModel):
    id_picture: int
    vec: str
    img_to_text: str


class ModelCreateSchema(BaseModel):
    id_picture: int
    vec: Optional[str] = None
    img_to_text: Optional[str] = None


class ModelUpdateSchema(BaseModel):
    id_picture: int
    vec: Optional[str] = None
    img_to_text: Optional[str] = None
