"""
Client for GetSmarter API Gateway.
"""

from getsmarter_api_clients.oauth import OAuthApiClient


class GetSmarterEnterpriseApiClient(OAuthApiClient):
    """
    Client to interface with the GetSmarter Enterprise API Gateway (GEAG).
    """

    def get_terms_and_policies(self):
        """
        Fetch and return the terms and policies from GEAG.

        Returns:
            Dict containing the keys 'privacyPolicy', 'websiteTermsOfUse',
            'studentTermsAndConditions', and 'cookiePolicy'.
        """
        url = f'{self.api_url}/terms'
        response = self.get(url)
        response.raise_for_status()
        return response.json()

    def create_allocation(self):
        """
        Create an allocation (enrollment) through GEAG.
        """
        return NotImplementedError()
