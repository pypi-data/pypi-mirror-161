from abc import ABC
from typing import Optional

from humps import camelize
from pydantic import BaseModel, root_validator


class BasePostModel(BaseModel, ABC):
    def json(self, *args, by_alias: bool = True, **kwargs) -> str:
        return super().json(*args, by_alias=by_alias, **kwargs)

    class Config:
        allow_population_by_field_name = True
        alias_generator = camelize


class TextData(BasePostModel):
    content: str


class ImageData(BasePostModel):
    raw: str
    filename: str


class BasePost(BasePostModel, ABC):
    pass


class TextOnlyPost(BasePost):
    text: TextData


class ImageOnlyPost(BasePost):
    image: ImageData


class TextAndImagePost(BasePost):
    text: TextData
    image: ImageData


class TextOrImagePost(BasePost):
    text: Optional[TextData] = None
    image: Optional[ImageData] = None

    @root_validator(pre=True)
    def check_if_at_least_one_present(cls, values):
        if "text" not in values and "image" not in values:
            raise ValueError("Any of text or image is required.")
        return values

    class Config:
        schema_extra = {
            "anyOf": [
                {"required": ["text"]},
                {"required": ["image"]},
            ]
        }


class TextWithOptionalImagePost(BasePost):
    text: TextData
    image: Optional[ImageData] = None


class ImageWithOptionalTextPost(BasePost):
    text: Optional[TextData] = None
    image: ImageData
