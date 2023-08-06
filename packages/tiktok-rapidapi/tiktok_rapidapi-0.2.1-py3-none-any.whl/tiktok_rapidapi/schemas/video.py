from datetime import datetime
from typing import Optional

from pydantic.class_validators import root_validator
from pydantic.fields import Field

from .content import TikTokContentModel
from .base import BaseModelORM
from .user import TikTokUserModel


class TikTokVideoVideoModel(BaseModelORM):
    cover: TikTokContentModel
    download_addr: TikTokContentModel
    origin_cover: TikTokContentModel
    animated_cover: TikTokContentModel
    dynamic_cover: TikTokContentModel
    play_addr: TikTokContentModel
    ai_dynamic_cover_bak: TikTokContentModel
    ai_dynamic_cover: TikTokContentModel
    play_addr_h264: Optional[TikTokContentModel]
    play_addr_bytevc1: Optional[TikTokContentModel]

    is_callback: bool
    ratio: str
    width: int
    height: int
    has_watermark: bool
    duration: int
    cdn_url_expired: int
    misc_download_addrs: Optional[str]
    meta: str


class TikTokVideoModel(BaseModelORM):
    id: str = Field(..., alias="aweme_id")
    created_time: datetime = Field(..., alias="create_time")  # -Дата и время поста
    description: str = Field(..., alias="desc")  # -Описание поста (включая эмодзи) (описание поста)
    play_count: int = Field(..., alias="play_count")  # -Кол-во просмотров клипа/поста
    share_count: int = Field(..., alias="share_count")  # - Количество репостов клипа
    likes_count: int = Field(..., alias="digg_count")  # -Количество лайков поста
    comment_count: Optional[int] = Field(None, alias="comment_count")  # -Количество комментариев поста
    share_url: Optional[str] = Field(None, alias="share_url")
    author: TikTokUserModel
    video: TikTokVideoVideoModel

    @root_validator(pre=True)
    def convert_data(cls, values):
        values.update(values.get("statistics", {})) # TODO: добавить отдельную модель для statistics

        return values
