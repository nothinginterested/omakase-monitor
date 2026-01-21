"""
Data models for Omakase Monitor
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TimeSlot:
    """Represents a restaurant reservation time slot"""
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    price: Optional[int] = None  # Price in JPY
    booking_url: Optional[str] = None
    available_seats: Optional[int] = None

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
        return f"https://omakase.in/ja/r/{self.slug}"

    @property
    def api_url(self) -> str:
        """API endpoint for time slots"""
        return f"https://omakase.in/api/v1/omakase/r/{self.slug}/online_stock_groups"


@dataclass
class NotificationData:
    """Data for email notification"""
    restaurant: Restaurant
    new_slots: list[TimeSlot]
    timestamp: datetime
