"""
Configuration classes used for configuring the Algora SDK.
"""
import os
from typing import Optional


class Auth:
    """
    Configuration class for getting the authentication information from the environment.
    """

    # Feature to keep values hidden from printing (not totally)
    # Allows for dynamic rendering of auth values
    @property
    def username(self) -> Optional[str]:
        return os.getenv("ALGORA_USER", None)

    @property
    def password(self) -> Optional[str]:
        return os.getenv("ALGORA_PWD", None)

    @property
    def access_token(self) -> Optional[str]:
        return os.getenv("ALGORA_ACCESS_TOKEN", None)

    @property
    def refresh_token(self) -> Optional[str]:
        return os.getenv("ALGORA_REFRESH_TOKEN", None)

    def can_authenticate(self) -> bool:
        """
        Check environment to see if the user provided enough info to authenticate requests.

        Returns:
            bool: A boolean that represents whether you can authenticate requests
        """
        auth_options = self.access_token or self.refresh_token or (self.username and self.password)
        return auth_options is not None

    def __eq__(self, other: "Auth"):
        return (
                self.access_token == other.access_token and
                self.username == self.username and
                self.password == self.password
        )


class EnvironmentConfig:
    """
    Configuration class for getting environment information.
    """
    urls: dict = {
        'algora': 'https://api.algoralabs.com',
        'keycloak': 'https://auth.algoralabs.com/auth/admin/realms/production',
        'fred': 'https://api.stlouisfed.org/fred'
    }
    auth_config: Auth = Auth()

    def get_url(self, key: str = "algora") -> str:
        return self.urls.get(key, self.urls["algora"])
