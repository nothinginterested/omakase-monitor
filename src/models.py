"""
Data models for Omakase Monitor
"""

from dataclasses import dataclass
from datetime import datetime

# Base URL for omakase.in
OMAKASE_BASE_URL = "https://omakase.in"


@dataclass
class TimeSlot:
    """Represents a restaurant reservation time slot"""
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    price: int | None = None  # Price in JPY
    booking_url: str | None = None
    available_seats: int | None = None

    def __hash__(self) -> int:
        return hash((self.date, self.time))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeSlot):
            return False
        return (self.date, self.time) == (other.date, other.time)


@dataclass
class Restaurant:
    """Represents a target restaurant"""
    name: str
    slug: str  # URL slug (e.g., "bu286225")
    url: str
    enabled: bool = True

    @property
    def detail_url(self) -> str:
        """Full restaurant detail page URL"""
        return f"{OMAKASE_BASE_URL}/ja/r/{self.slug}"

    @property
    def api_url(self) -> str:
        """API endpoint for time slots"""
        return f"{OMAKASE_BASE_URL}/api/v1/omakase/r/{self.slug}/online_stock_groups"


@dataclass
class NotificationData:
    """Data for email notification"""
    restaurant: Restaurant
    new_slots: list[TimeSlot]
    timestamp: datetime
