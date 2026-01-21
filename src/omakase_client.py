"""
HTTP client for omakase.in API
"""

import logging
import httpx
from src.models import TimeSlot

logger = logging.getLogger(__name__)


class OmakaseClient:
    """HTTP client for omakase.in"""

    def __init__(self):
        self.session: httpx.AsyncClient | None = None
        self.cookies: dict = {}

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
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def login(self, email: str, password: str) -> bool:
        """Login to omakase.in"""
        # TODO: Implement login logic
        logger.info(f"Login attempt for {email} (placeholder)")
        return False

    async def get_time_slots(self, restaurant_slug: str) -> list[TimeSlot]:
        """Fetch available time slots for a restaurant"""
        # TODO: Implement API call
        logger.info(f"Fetching slots for {restaurant_slug} (placeholder)")
        return []
