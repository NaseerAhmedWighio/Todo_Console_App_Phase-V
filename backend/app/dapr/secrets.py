"""
Dapr Secrets Client
Retrieves secrets from Dapr secret stores (Kubernetes Secrets, Azure Key Vault, etc.)
"""

import logging
from typing import Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class DaprSecretsClient:
    """Client for Dapr Secrets API"""

    def __init__(self, dapr_http_port: int = 3500, secret_store_name: str = "kubernetes-secrets"):
        self.dapr_http_port = dapr_http_port
        self.secret_store_name = secret_store_name
        self.base_url = f"http://localhost:{dapr_http_port}"

    async def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieve a secret from Dapr secret store

        Args:
            secret_name: Name of the secret

        Returns:
            Secret value or None if not found
        """
        url = f"{self.base_url}/v1.0/secrets/{self.secret_store_name}/{secret_name}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 404:
                    logger.warning(f"Secret {secret_name} not found")
                    return None
                response.raise_for_status()
                data = response.json()
                # Dapr returns {secret_name: value}
                return data.get(secret_name)
        except httpx.HTTPError as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting secret {secret_name}: {e}")
            return None

    async def get_all_secrets(self) -> Dict[str, str]:
        """
        Retrieve all secrets from Dapr secret store

        Returns:
            Dictionary of all secrets
        """
        url = f"{self.base_url}/v1.0/secrets/{self.secret_store_name}/bulk"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get bulk secrets: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting bulk secrets: {e}")
            return {}


# Global instance
_secrets_client: Optional[DaprSecretsClient] = None


def get_secrets_client() -> DaprSecretsClient:
    """Get or create the global Dapr Secrets client instance"""
    global _secrets_client
    if _secrets_client is None:
        _secrets_client = DaprSecretsClient()
    return _secrets_client
