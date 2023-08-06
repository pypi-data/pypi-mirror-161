import json
import logging
from typing import Optional

from ..connectors.api_connector import ApiConnector
from ..utils import utils
from ..utils.constants.api_graph_constants import (  # Fields; Operations
    ACCESS_TOKEN,
    GET_ACCOUNTS,
    GET_BUSINESS_ACCOUNT,
    INSTAGRAM_BUSINESS_ACCOUNT,
    LONG_LIVED_TOKEN,
    MEDIA_FIELDS,
    META_API_GRAPH_URL,
    META_API_GRAPH_VERSION,
    RESENT_MEDIA,
    SEARCH_IG_HASHTAG,
    TOP_MEDIA,
)
from ..utils.constants.constants import DATA, GET, ID, META_API_SECRET_KEY, META_APP_ID


class MetaApiConnector(ApiConnector):
    api_url = META_API_GRAPH_URL + META_API_GRAPH_VERSION
    api_token = "{prefix}access_token={token}"
    token = ""

    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token

    def __add_token__(
        self, request_url: str, token: str, prefix: Optional[str] = None
    ) -> str:
        if "fields" in request_url:
            token_field = self.api_token.format(prefix="&", token=token)
        else:
            token_field = self.api_token.format(prefix="?", token=token)
        if prefix:
            token_field = self.api_token.format(prefix=prefix, token=token)

        return request_url + token_field

    def get_long_lived_token(self, access_token: Optional[str] = None):
        """
        Description
        ----------
        Given a normal Facbook account token, this function generates a long lived
        token. Validity of about 60 days.

        Arguments
        ---------
        access_token: str
            Normal Facebook token

        Return
        -------
        token: str | error message

        """
        request_url = self.api_url
        request_url += LONG_LIVED_TOKEN.format(
            app_id=META_APP_ID, api_key_secret=META_API_SECRET_KEY, token=self.token
        )
        response = self.api_request(
            request_url=request_url,
            operation=GET,
        )
        content = json.loads(response.content)
        if response.status_code == 200 and ACCESS_TOKEN in content.keys():
            return content[ACCESS_TOKEN]
        else:
            utils.log_api_execption(
                function_name=self.get_long_lived_token.__name__,
                code_status=response.status_code,
                details=content,
            )
            return content

    def get_ig_account_info_by_token(self):
        """
        Description
        ----------
        Given a Facbook account token, this function searches if there is a
        business account id related with this account.

        Arguments
        ---------
        token: str
            Facebook token

        Return
        -------
        is_business: bool, str | bool, error_message

        """
        logging.info("Obteniendo app id")
        request_url = self.api_url
        request_url += GET_ACCOUNTS
        request_url = self.__add_token__(request_url=request_url, token=self.token)
        response = self.api_request(
            request_url=request_url,
            operation=GET,
        )
        content = json.loads(response.content)
        # TODO: use a http status code codification
        if response.status_code == 200:
            if DATA in content.keys() and type(content[DATA]) is list:
                for account in content[DATA]:
                    is_business, business_id = self.get_ig_business_by_account_id(
                        account_id=account["id"], token=self.token
                    )
                    if is_business:
                        break

            return True, business_id
        else:
            utils.log_api_execption(
                function_name=self.get_ig_account_info_by_token.__name__,
                code_status=response.status_code,
                details=content,
            )
            return False, None

    def get_ig_business_by_account_id(self, account_id: str, token: str):
        """
        Description
        ----------
        Given a Facbook account id, this function searches if there is a
        business account id related with this account.

        Arguments
        ---------
        account_id: str
            Id of the app used to do the requests
        token: str
            Facebook token

        Return
        -------
        instagram_business_account: bool, str | bool, error_message

        """
        request_url = self.api_url
        request_url += GET_BUSINESS_ACCOUNT.format(account_id=account_id)
        request_url = self.__add_token__(request_url=request_url, token=token)
        response = self.api_request(
            request_url=request_url,
            operation=GET,
        )
        content = json.loads(response.content)
        if response.status_code == 200 and INSTAGRAM_BUSINESS_ACCOUNT in content.keys():
            return True, content[INSTAGRAM_BUSINESS_ACCOUNT][ID]
        else:
            logging.error("get_ig_business_by_account_id:")
            logging.debug(content)
            return False, None

    def search_ig_hashtag(self, ig_business_account_id: str, query: str):
        """
        Description
        ----------
        Given a business account id, and a query, searches the term and returns
        an hashtag id

        Arguments
        ---------
        ig_business_account_id: str
            The ID of the IG User performing the request
        query: str
            The hashtag name to query
        Return
        -------
        ig_hashtag_id: bool, str | bool, error_message

        """
        request_url = self.api_url
        request_url += SEARCH_IG_HASHTAG.format(
            ig_business_account_id=ig_business_account_id, query=query
        )
        request_url = self.__add_token__(
            request_url=request_url, token=self.token, prefix="&"
        )
        response = self.api_request(
            request_url=request_url,
            operation=GET,
        )
        content = json.loads(response.content)
        if response.status_code == 200 and DATA in content.keys():
            return True, content[DATA][0][ID]  # First Term
        else:
            logging.error("search_ig_hashtag:")
            logging.error(content)
            return False, None

    def get_ig_recent_media(self, ig_business_account_id: str, hashtag_id: str):
        """
        Description
        ----------
        Given a hashtag id, and a business account id, searches the term and
        returns the resent media of the hashtag

        Arguments
        ---------
        ig_business_account_id: str
            The ID of the IG User performing the request
        hashtag_id: str
            The hashtag name to query
        Return
        -------
        ig_recent_media_data: bool, dict | bool, error_message

        """
        request_url = self.api_url
        request_url += RESENT_MEDIA.format(
            hashtag_id=hashtag_id,
            fields=MEDIA_FIELDS,
            ig_business_account_id=ig_business_account_id,
        )
        request_url = self.__add_token__(request_url=request_url, token=self.token)
        response = self.api_request(
            request_url=request_url,
            operation=GET,
        )
        content = json.loads(response.content)
        if response.status_code == 200 and DATA in content.keys():
            return True, content[DATA]
        else:
            logging.error("get_ig_recent_media:")
            logging.error(content)
            return False, None

    def get_ig_top_media(self, ig_business_account_id: str, hashtag_id: str):
        """
        Description
        ----------
        Given a hashtag id, and a business account id, searches the term and
        returns the resent media of the hashtag

        Arguments
        ---------
        ig_business_account_id: str
            The ID of the IG User performing the request
        hashtag_id: str
            The hashtag name to query
        Return
        -------
        ig_top_media_data: bool, dict | bool, error_message

        """
        request_url = self.api_url
        request_url += TOP_MEDIA.format(
            hashtag_id=hashtag_id,
            fields=MEDIA_FIELDS,
            ig_business_account_id=ig_business_account_id,
        )
        request_url = self.__add_token__(request_url=request_url, token=self.token)
        response = self.api_request(
            request_url=request_url,
            operation=GET,
        )
        content = json.loads(response.content)
        if response.status_code == 200 and DATA in content.keys():
            return True, content[DATA]
        else:
            logging.error("get_ig_top_media:")
            logging.error(content)
            return False, None
