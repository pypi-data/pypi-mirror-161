import imp
import os
from typing import Optional

from ..connectors.api_graph_connector import MetaApiConnector
from ..utils.constants.api_graph_constants import MEDIA_FIELDS
from ..utils.constants.constants import CSV, JSON, MEDIA_DIR
from ..utils.ig_utils import get_shortcode_from_permalink
from ..utils.utils import download_image, safe_data_on_csv, save_data_on_json


def generate_long_lived_token(access_token: str) -> str:
    """
    Description
    ----------
    Given a normal Facbook account token, this function generates a long lived
    token. Validity of about 60 days.

    Return
    -------
    token: str | error message

    """
    meta_connector = MetaApiConnector(token=access_token)
    long_lived_token = meta_connector.get_long_lived_token()
    return long_lived_token


def search_hashtag(query: str, token: str):
    meta_connector = MetaApiConnector(token=token)
    found_bs_ac, bs_id = meta_connector.get_ig_account_info_by_token()
    if found_bs_ac:
        search_succcess, hashtag_id = meta_connector.search_ig_hashtag(
            ig_business_account_id=bs_id, query=query
        )
        if not search_succcess:
            return
        resent_success, resent_media_response = meta_connector.get_ig_recent_media(
            ig_business_account_id=bs_id, hashtag_id=hashtag_id
        )
        if resent_success:
            safe_data_on_csv(
                path="resent_media.csv",
                data=resent_media_response,
                columns=MEDIA_FIELDS.split(","),
            )
        top_succcess, top_media_response = meta_connector.get_ig_top_media(
            ig_business_account_id=bs_id, hashtag_id=hashtag_id
        )
        if top_succcess:
            safe_data_on_csv(
                path="top_media.csv",
                data=top_media_response,
                columns=MEDIA_FIELDS.split(","),
            )
    else:
        return "Not found"


def download_recent_media_ig(query: str, token: str, file_type: str):
    """
    Description
    ----------
    Given a query, this function returns a list of media from hashtag IG accoount

    Arguments
    ---------
    query: str
        Hashtag name to search and download
    token: str
        Facebook token
    file_type: str
        Type of file to save the media info (json, csv)

    Return
    -------
        None

    """
    meta_connector = MetaApiConnector(token=token)
    found_bs_ac, bs_id = meta_connector.get_ig_account_info_by_token()
    if found_bs_ac:
        search_succcess, hashtag_id = meta_connector.search_ig_hashtag(
            ig_business_account_id=bs_id, query=query
        )
        if not search_succcess:
            return
        resent_success, resent_media_response = meta_connector.get_ig_recent_media(
            ig_business_account_id=bs_id, hashtag_id=hashtag_id
        )
        if not resent_success:
            return
        if file_type == CSV:
            safe_data_on_csv(
                path="resent_media.csv",
                data=resent_media_response,
                columns=MEDIA_FIELDS.split(","),
            )
        elif file_type == JSON:
            save_data_on_json(path="resent_media.json", data=resent_media_response)
    else:
        return


def download_recent_media_ig_by_post(
    query: str, token: str, download_path: Optional[str] = None
):
    """
    Description
    ----------
    Given a query, this function downloads the images and metadata from IG API.

    Arguments
    ---------
    query: str
        Hashtag name to search and download
    token: str
        Facebook token
    download_path: str
        Path to download the json data with the shortcode as name, it download:
            - Image: shortcode.jpg
            - metadata: shortcode.json

    Return
    -------
        None

    """
    meta_connector = MetaApiConnector(token=token)
    found_bs_ac, bs_id = meta_connector.get_ig_account_info_by_token()
    if found_bs_ac:
        search_succcess, hashtag_id = meta_connector.search_ig_hashtag(
            ig_business_account_id=bs_id, query=query
        )
        if not search_succcess:
            return
        resent_success, resent_media_response = meta_connector.get_ig_recent_media(
            ig_business_account_id=bs_id, hashtag_id=hashtag_id
        )
        if not resent_success:
            return

        if not os.path.exists(MEDIA_DIR):
            os.makedirs(MEDIA_DIR)
        for post in resent_media_response:
            if post["media_type"] != "IMAGE":
                continue
            shortcode = get_shortcode_from_permalink(permalink=post["permalink"])

            if download_path:
                json_path = download_path + "\\" + shortcode + ".json"
            else:
                json_path = MEDIA_DIR + "\\" + shortcode + ".json"

            save_data_on_json(path=json_path, data=post)

            if download_path:
                image_path = download_path + "\\" + shortcode + ".jpg"
            else:
                image_path = MEDIA_DIR + "\\" + shortcode + ".jpg"

            download_image(url=post["media_url"], filename=image_path)
    else:
        return
