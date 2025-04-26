"""
OpenSymbols Secret Fetcher

This module provides functionality to fetch the shared secret from the
OpenSymbols API website, which is required for authentication.
"""

import logging
import os
import re
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class OpenSymbolsSecretFetcher:
    """
    Fetches the shared secret from the OpenSymbols API website using browser automation.

    The shared secret is required to generate access tokens for the OpenSymbols API.
    This secret changes periodically, so this class provides functionality to
    fetch the current secret programmatically.
    """

    API_URL = "https://www.opensymbols.org/api"

    def __init__(self):
        """Initialize the OpenSymbolsSecretFetcher."""
        pass

    def fetch_secret(self) -> Optional[str]:
        """
        Fetch the current shared secret from the OpenSymbols API page.

        Returns:
            str: The current shared secret, or None if it could not be fetched.
        """
        try:
            logger.info("Fetching OpenSymbols shared secret using Selenium")

            # Configure Chrome options for headless operation
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            )

            # Initialize the WebDriver
            driver = webdriver.Chrome(options=chrome_options)

            try:
                # Load the page
                driver.get(self.API_URL)

                # Wait for the page to load and the token field to be populated
                # Try multiple selectors since we're not certain about the exact ID
                wait = WebDriverWait(driver, 10)

                # Look for input elements that might contain the token
                potential_selectors = [
                    (By.ID, "token"),
                    (By.NAME, "secret"),
                    (By.NAME, "token"),
                    (By.CSS_SELECTOR, "input[name*='token']"),
                    (By.CSS_SELECTOR, "input[name*='secret']"),
                    (By.CSS_SELECTOR, "input[id*='token']"),
                    (By.CSS_SELECTOR, "input[id*='secret']"),
                    (By.CSS_SELECTOR, "input[placeholder*='secret']"),
                    (By.CSS_SELECTOR, ".api_token_holder input"),
                    (By.CSS_SELECTOR, "form[action*='token'] input"),
                ]

                element = None
                for selector_type, selector in potential_selectors:
                    try:
                        element = wait.until(
                            EC.presence_of_element_located((selector_type, selector))
                        )
                        if element and element.get_attribute("value"):
                            logger.info(
                                f"Found token using selector: {selector_type} = {selector}"
                            )
                            break
                    except TimeoutException:
                        continue

                if not element:
                    # If we couldn't find the element with specific selectors, let's try to find
                    # any input that has a value that looks like a token
                    logger.info("Trying to find any input with a token-like value")
                    inputs = driver.find_elements(By.TAG_NAME, "input")
                    for input_elem in inputs:
                        value = input_elem.get_attribute("value")
                        if value and (value.startswith("temp:") or len(value) > 20):
                            element = input_elem
                            logger.info(
                                f"Found potential token input with value: {value[:10]}..."
                            )
                            break

                if not element:
                    logger.error("Could not find the secret input field on the page")
                    # Let's grab the page HTML for debugging
                    logger.debug(f"Page HTML: {driver.page_source[:1000]}...")
                    return None

                # Extract the value
                secret = element.get_attribute("value")

                if not secret:
                    logger.error("Secret input field found but value is empty")
                    return None

                logger.info(
                    f"Successfully fetched OpenSymbols shared secret: {secret[:10]}..."
                )
                return secret

            finally:
                # Always close the driver to prevent resource leaks
                driver.quit()

        except Exception as e:
            logger.error(f"Error fetching OpenSymbols shared secret: {str(e)}")
            return None


def get_open_symbols_secret() -> Optional[str]:
    """
    Convenience function to fetch the OpenSymbols shared secret.

    Returns:
        str: The current shared secret, or None if it could not be fetched.
    """
    fetcher = OpenSymbolsSecretFetcher()
    return fetcher.fetch_secret()


def update_env_with_new_secret() -> dict:
    """
    Fetch a new OpenSymbols shared secret and update the .env file.

    Returns:
        dict: A dictionary containing success status and a message.
    """
    # Get the new secret
    new_secret = get_open_symbols_secret()

    if not new_secret:
        logger.error("Failed to fetch new secret, cannot update .env file")
        return {"success": False, "message": "Failed to fetch new secret"}

    try:
        # Path to .env file (assuming it's in the project root)
        env_path = os.path.join(os.getcwd(), ".env")

        if not os.path.exists(env_path):
            logger.error(f".env file not found at {env_path}")
            return {"success": False, "message": ".env file not found"}

        # Read the current .env file
        with open(env_path, "r") as file:
            env_content = file.read()

        # Check if OPEN_SYMBOLS_SECRET_KEY already exists in the file
        if "OPEN_SYMBOLS_SECRET_KEY" in env_content:
            # Replace the existing value using regex
            updated_content = re.sub(
                r"OPEN_SYMBOLS_SECRET_KEY=.*",
                f"OPEN_SYMBOLS_SECRET_KEY={new_secret}",
                env_content,
            )
        else:
            # Add the key if it doesn't exist
            updated_content = f"{env_content}\nOPEN_SYMBOLS_SECRET_KEY={new_secret}"

        # Write the updated content back to the .env file
        with open(env_path, "w") as file:
            file.write(updated_content)

        logger.info("Successfully updated OPEN_SYMBOLS_SECRET_KEY in .env file")
        return {
            "success": True,
            "message": "Successfully updated OpenSymbols secret key",
            "secret_preview": f"{new_secret[:10]}...",
        }

    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")
        return {"success": False, "message": f"Error updating .env file: {str(e)}"}


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(level=logging.INFO)

    secret = get_open_symbols_secret()
    print(f"Secret: {secret}")
