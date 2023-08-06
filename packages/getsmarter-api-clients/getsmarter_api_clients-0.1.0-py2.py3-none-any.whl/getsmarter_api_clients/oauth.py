
"""
Base API client that handles authentication.
"""

import datetime
import logging

import pytz
import requests
from edx_django_utils.cache import TieredCache
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

logger = logging.getLogger(__name__)


class OAuthApiClient(requests.Session):
    """
    Base API client that authenticates using the provided client credentials.
    """

    def __init__(
        self,
        client_id,
        client_secret,
        provider_url,
        api_url,
        **kwargs
    ):
        """
        Initialize an instance of the OAuthApiClient.
        """
        super().__init__(**kwargs)

        self.oauth_client_id = client_id
        self.oauth_client_secret = client_secret
        self.oauth_provider_url = provider_url
        self.api_url = api_url

    @property
    def access_token_cache_key(self):
        """
        Return the cache key for the access token.
        """
        return 'get_smarter_api_client.access_token_response.{}'.format(self.oauth_client_id)

    def _get_cached_access_token(self):
        """
        Return the cached access token if it is not expired.
        """
        cached_response = TieredCache.get_cached_response(self.access_token_cache_key)
        if cached_response.is_found:
            cached_value = cached_response.value
            expires_at = cached_value['expires_at']
            if datetime.datetime.now(pytz.utc).timestamp() < expires_at:
                return cached_value['access_token']

        return None

    def _get_access_token(self):
        """
        Return the access token required for making calls.
        """
        cached_token = self._get_cached_access_token()
        if cached_token:
            return cached_token

        try:
            client = BackendApplicationClient(client_id=self.oauth_client_id)
            oauth = OAuth2Session(client=client)
            token_response = oauth.fetch_token(
                token_url=f'{self.oauth_provider_url}/oauth2/token',
                client_secret=self.oauth_client_secret
            )
            TieredCache.set_all_tiers(self.access_token_cache_key, token_response, token_response['expires_in'])
            return token_response['access_token']
        except Exception as ex:  # pylint: disable=broad-except
            logger.exception(ex)
            return None

    def _ensure_authentication(self):
        """
        Add the required headers for authentication.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0',  # GetSmarter blocks the python-requests user agent for certain requests
            'Authorization': 'Bearer ' + self._get_access_token(),
        }
        self.headers.update(headers)

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """
        Override Session.request to ensure that the session is authenticated.

        Note: Typically, users of the client won't call this directly, but will
        instead use Session.get or Session.post.

        """
        self._ensure_authentication()
        return super().request(method, url, **kwargs)
