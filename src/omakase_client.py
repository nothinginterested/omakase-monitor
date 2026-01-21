"""
HTTP client for omakase.in API
"""

import json
import logging
import re
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from src.models import TimeSlot, OMAKASE_BASE_URL
from src.utils import retry_on_failure, random_delay

logger = logging.getLogger(__name__)

COOKIES_FILE = "cookies.json"


class OmakaseClient:
    """HTTP client for omakase.in"""

    def __init__(self, cookies_file: str = COOKIES_FILE):
        self.session: httpx.AsyncClient | None = None
        self.cookies: dict = {}
        self.cookies_file = Path(cookies_file)
        self.is_logged_in = False

    async def __aenter__(self):
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36"
        )
        accept_header = (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,*/*;q=0.8"
        )

        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": user_agent,
                "Accept": accept_header,
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            }
        )

        # Load cookies from file if they exist
        self._load_cookies()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    def _load_cookies(self) -> None:
        """Load cookies from file"""
        if self.cookies_file.exists():
            try:
                with open(self.cookies_file, 'r') as f:
                    self.cookies = json.load(f)
                if self.session:
                    self.session.cookies.update(self.cookies)
                logger.info("Loaded cookies from file")
                self.is_logged_in = True
            except Exception as e:
                logger.warning(f"Failed to load cookies: {e}")
                self.cookies = {}

    def _save_cookies(self) -> None:
        """Save cookies to file"""
        try:
            if self.session:
                self.cookies = dict(self.session.cookies)
            with open(self.cookies_file, 'w') as f:
                json.dump(self.cookies, f)
            logger.info("Saved cookies to file")
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")

    async def _get_csrf_token(self) -> str | None:
        """Extract CSRF token from login page"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        try:
            response = await self.session.get(f"{OMAKASE_BASE_URL}/users/sign_in")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for CSRF token in meta tag
            csrf_meta = soup.find('meta', attrs={'name': 'csrf-token'})
            if csrf_meta and csrf_meta.get('content'):
                return csrf_meta['content']

            # Look for CSRF token in hidden input field
            csrf_input = soup.find('input', attrs={'name': 'authenticity_token'})
            if csrf_input and csrf_input.get('value'):
                return csrf_input['value']

            logger.error("CSRF token not found in login page")
            return None

        except Exception as e:
            logger.error(f"Failed to get CSRF token: {e}", exc_info=True)
            return None

    @retry_on_failure(max_retries=3, backoff_factor=2.0)
    async def login(self, email: str, password: str) -> bool:
        """
        Login to omakase.in

        Args:
            email: User email
            password: User password

        Returns:
            True if login successful, False otherwise
        """
        if not self.session:
            raise RuntimeError("Session not initialized")

        # If already logged in with saved cookies, verify they're still valid
        if self.is_logged_in:
            logger.info("Using saved session")
            return True

        try:
            logger.info(f"Attempting login for {email}")

            # Get CSRF token
            csrf_token = await self._get_csrf_token()
            if not csrf_token:
                logger.error("Cannot proceed without CSRF token")
                return False

            # Add small delay to mimic human behavior
            await random_delay(1.0, 2.0)

            # Prepare login data
            login_data = {
                'authenticity_token': csrf_token,
                'user[email]': email,
                'user[password]': password,
                'user[remember_me]': '1',
                'commit': 'ログイン'  # "Login" in Japanese
            }

            # Submit login form
            response = await self.session.post(
                f"{OMAKASE_BASE_URL}/users/sign_in",
                data=login_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': f"{OMAKASE_BASE_URL}/users/sign_in"
                }
            )

            # Check if login was successful
            # Successful login usually redirects to home page or dashboard
            if response.status_code == 200:
                # Check if we're still on login page (failed login)
                if '/users/sign_in' in str(response.url):
                    logger.error("Login failed: Still on login page")
                    return False

                # Save cookies for future use
                self._save_cookies()
                self.is_logged_in = True
                logger.info("Login successful")
                return True
            else:
                logger.error(f"Login failed with status {response.status_code}")
                return False

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during login: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}", exc_info=True)
            return False

    @retry_on_failure(max_retries=3, backoff_factor=2.0)
    async def get_time_slots(self, restaurant_slug: str) -> list[TimeSlot]:
        """
        Fetch available time slots for a restaurant

        Args:
            restaurant_slug: Restaurant URL slug

        Returns:
            List of available TimeSlot objects
        """
        if not self.session:
            raise RuntimeError("Session not initialized")

        if not self.is_logged_in:
            logger.warning("Not logged in, time slots may not be available")

        try:
            # Call the API endpoint
            api_url = (
                f"{OMAKASE_BASE_URL}/api/v1/omakase/r/"
                f"{restaurant_slug}/online_stock_groups"
            )

            logger.debug(f"Fetching time slots from {api_url}")
            response = await self.session.get(api_url)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # TODO: Parse the actual API response structure
            # This is a placeholder - actual structure needs to be determined
            logger.info(
                f"Fetched time slots for {restaurant_slug}: "
                f"{len(data) if isinstance(data, list) else 'unknown'} items"
            )

            # For now, return empty list until we know the API structure
            return []

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Authentication required - login session may have expired")
                self.is_logged_in = False
            logger.error(
                f"HTTP error fetching time slots: {e.response.status_code}"
            )
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error fetching time slots: {e}", exc_info=True
            )
            raise
