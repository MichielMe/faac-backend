"""
Open Symbols API Client

This module provides a client for interacting with the Open Symbols API,
which offers access to open-licensed communication symbols.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from app.core import settings

logger = logging.getLogger(__name__)


class OpenSymbolsClient:
    """
    Client for the Open Symbols API.

    This client handles authentication, searching for symbols, and managing
    token expiration and request throttling.
    """

    # Update URLs to include www subdomain as seen in the browser request
    BASE_URL = "https://www.opensymbols.org/api/v2/"
    TOKEN_URL = "https://www.opensymbols.org/api/v2/token"

    # Browser-like headers that mimic the AJAX request
    HEADERS = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://www.opensymbols.org",
        "referer": "https://www.opensymbols.org/api",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (compatible; FAAC/1.0)",
    }

    # Skin tone mapping for symbols that support skin variations
    SKIN_TONES = {
        "light": "1f3fb",
        "medium-light": "1f3fc",
        "medium": "1f3fd",
        "medium-dark": "1f3fe",
        "dark": "1f3ff",
    }

    def __init__(self):
        """
        Initialize the OpenSymbols client.

        Args:
            shared_secret: The shared secret provided by Open Symbols.
                          This should be kept secure and not exposed in client-side code.
        """
        self.shared_secret = settings.OPEN_SYMBOLS_SECRET_KEY
        self.access_token = None

    def _get_access_token(self) -> str:
        """
        Generate an access token using the shared secret.

        Returns:
            str: The access token for API requests.

        Raises:
            requests.exceptions.HTTPError: If the token request fails.
        """
        try:
            # Send the secret as JSON payload with browser-like headers
            response = requests.post(
                self.TOKEN_URL,
                json={"secret": self.shared_secret},
                headers=self.HEADERS,
            )

            # Debug information
            logger.info(f"Token request status: {response.status_code}")

            response.raise_for_status()

            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                raise ValueError("Failed to obtain access token")

            self.access_token = access_token
            return access_token
        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            raise

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """
        Make an authenticated request to the API.

        Args:
            endpoint: API endpoint to call.
            params: Query parameters for the request.

        Returns:
            The JSON response from the API.

        Raises:
            ValueError: If the request fails due to authentication or throttling issues.
            requests.exceptions.HTTPError: For other HTTP errors.
        """
        url = urljoin(self.BASE_URL, endpoint)

        # Generate a token if we don't have one
        if not self.access_token:
            self.access_token = self._get_access_token()

        params["access_token"] = self.access_token

        # Use the browser-like headers for all requests
        headers = self.HEADERS.copy()

        try:
            response = requests.get(url, params=params, headers=headers)

            # Handle token expiration
            if response.status_code == 401:
                error_data = response.json()
                if error_data.get("token_expired", True):
                    logger.info("Access token expired. Generating a new one.")
                    self.access_token = self._get_access_token()
                    params["access_token"] = self.access_token
                    response = requests.get(url, params=params, headers=headers)

            # Handle throttling
            if response.status_code == 429:
                error_data = response.json()
                if error_data.get("throttled", False):
                    raise ValueError(
                        "Request throttled. Try again later or reduce request frequency."
                    )

            # Log the response details for debugging
            logger.debug(
                f"OpenSymbols API request to {url}: status={response.status_code}"
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {endpoint}: {str(e)}")
            raise

    def search_symbols(
        self,
        query: str,
        locale: str = "en",
        safe: int = 1,
        repo_key: Optional[str] = None,
        favor_repo: Optional[str] = None,
        high_contrast: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search for symbols matching the given criteria.

        Args:
            query: Search term(s).
            locale: Language/locale to search (two-character code, default 'en').
            safe: Safe search enabled (1) or disabled (0).
            repo_key: Optional repository key to limit results to a specific library.
            favor_repo: Optional repository key to favor results from a specific library.
            high_contrast: Whether to favor high-contrast results.

        Returns:
            List of symbol dictionaries matching the search criteria.
        """
        # Build the query string with optional modifiers
        modified_query = query

        if repo_key:
            modified_query += f" repo:{repo_key}"

        if favor_repo:
            modified_query += f" favor:{favor_repo}"

        if high_contrast:
            modified_query += " hc:1"

        params = {
            "q": modified_query,
            "locale": locale,
            "safe": safe,
            "extension": "png",
        }

        try:
            return self._make_request("symbols", params)
        except Exception as e:
            logger.error(f"OpenSymbols API error: {str(e)}")
            logger.warning(
                "The OpenSymbols API appears to be inaccessible directly. "
                "Their API may only be accessible through their website interface. "
                "Consider contacting OpenSymbols for proper API access."
            )
            # Return an empty list instead of raising an exception
            return []

    def get_symbol_with_skin_tone(
        self, symbol: Dict[str, Any], skin_tone: str
    ) -> Dict[str, Any]:
        """
        Get a symbol with the specified skin tone if available.

        Args:
            symbol: The symbol dictionary from the API.
            skin_tone: The desired skin tone ('light', 'medium-light', 'medium',
                       'medium-dark', or 'dark').

        Returns:
            Dict: Modified symbol with updated image_url for the requested skin tone.

        Raises:
            ValueError: If the symbol doesn't support skin tones or the skin tone is invalid.
        """
        if not symbol.get("skins", False):
            raise ValueError("This symbol does not support skin tone variations")

        if skin_tone not in self.SKIN_TONES:
            valid_tones = ", ".join(self.SKIN_TONES.keys())
            raise ValueError(f"Invalid skin tone. Valid options are: {valid_tones}")

        # Create a copy of the symbol to avoid modifying the original
        modified_symbol = symbol.copy()
        image_url = symbol.get("image_url", "")

        # Handle the two different patterns mentioned in the documentation
        if "varianted-skin" in image_url:
            modified_symbol["image_url"] = image_url.replace(
                "varianted-skin", f"variant-{skin_tone}"
            )
        elif "-var" in image_url and "UNI" in image_url:
            var_pattern = re.search(r"-var([^UNI]+)UNI", image_url)
            if var_pattern:
                var_text = var_pattern.group(0)
                skin_hex = self.SKIN_TONES[skin_tone]
                modified_symbol["image_url"] = image_url.replace(
                    var_text, f"-{skin_hex}"
                )

        return modified_symbol
