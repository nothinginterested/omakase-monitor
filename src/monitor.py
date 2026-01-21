"""
Core monitoring service
"""

import logging
from typing import Dict, Set
from src.models import Restaurant, TimeSlot
from src.config import Config

logger = logging.getLogger(__name__)


class MonitorService:
    """Main monitoring service"""

    def __init__(self, config: Config):
        self.config = config
        self.previous_slots: Dict[str, Set[TimeSlot]] = {}
        logger.info(
            f"MonitorService initialized with {len(config.restaurants)} restaurants"
        )

    async def start(self):
        """Start monitoring"""
        logger.info("Monitor service started (placeholder)")
        # TODO: Implement monitoring loop
        pass

    def detect_new_slots(
        self, restaurant: Restaurant, current_slots: Set[TimeSlot]
    ) -> Set[TimeSlot]:
        """Detect newly available time slots"""
        previous = self.previous_slots.get(restaurant.slug, set())
        new_slots = current_slots - previous
        self.previous_slots[restaurant.slug] = current_slots
        return new_slots
