from pydantic.class_validators import root_validator
from pydantic.fields import Field

from .base import BaseModelORM
from . import TikTokUserModel


class TikTokCommentModel(BaseModelORM):
    id: str = Field(..., alias="cid")

    text: str = Field(..., alias="text")
    likes_count: int = Field(..., alias="digg_count")

    video_id: str = Field(..., alias="aweme_id")

    user: TikTokUserModel = Field(..., alias="user")
