from typing import Optional

from ..controllers.meta_controller import (
    download_recent_media_ig,
    download_recent_media_ig_by_post,
)
from ..utils.constants.constants import TOKEN


class Instagram:
    """
    Description
    ----------
    Allows the use of functions related with Instagram platform


    """

    token = None

    def __init__(self, token: Optional[str] = None) -> None:
        if token:
            self.token = token
        else:
            self.token = TOKEN

    def download_recent_all_media(self, query: str, file_type: str):
        download_recent_media_ig(query=query, token=self.token, file_type=file_type)

    def download_recent_media_ig_by_post(self, query: str):
        download_recent_media_ig_by_post(
            query=query,
            token=self.token,
        )
