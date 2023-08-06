from typing import List
from typing import Optional

from pydantic.class_validators import root_validator
from pydantic.fields import Field

from .base import BaseModelORM


class TikTokContentModel(BaseModelORM):
    uri: str
    url_list: List[str]
    width: Optional[int]
    height: Optional[int]
    data_size: Optional[int]
    file_hash: Optional[str]
    file_cs: Optional[str]
    url_key: Optional[str]
