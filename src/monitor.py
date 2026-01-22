"""
Core monitoring service
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Set
from src.models import Restaurant, TimeSlot, NotificationData
from src.config import Config, RestaurantConfig
from src.omakase_client import OmakaseClient
from src.notifier import GmailNotifier
from src.utils import random_delay

logger = logging.getLogger(__name__)


class MonitorService:
    """Main monitoring service"""

    def __init__(self, config: Config):
        self.config = config
        self.previous_slots: Dict[str, Set[TimeSlot]] = {}
        self.notifier = GmailNotifier(
            smtp_server=config.gmail.smtp_server,
            smtp_port=config.gmail.smtp_port,
            sender_email=config.gmail.sender_email,
            app_password=config.gmail.app_password
        )
        logger.info(
            f"MonitorService initialized with {len(config.restaurants)} restaurants"
        )

    async def start(self) -> None:
        """
        Start monitoring service

        This is the main entry point that runs a single monitoring cycle.
        For continuous monitoring, this should be called repeatedly by a scheduler.
        """
        logger.info("=" * 60)
        logger.info("Starting monitoring cycle")
        logger.info("=" * 60)

        # Get enabled restaurants
        enabled_restaurants = [
            r for r in self.config.restaurants if r.enabled
        ]

        if not enabled_restaurants:
            logger.warning("No enabled restaurants to monitor")
            return

        logger.info(f"Monitoring {len(enabled_restaurants)} restaurants")

        # Use omakase client
        async with OmakaseClient() as client:
            # Login
            login_success = await client.login(
                self.config.omakase.email,
                self.config.omakase.password
            )

            if not login_success:
                logger.error("Failed to login to omakase.in")
                return

            # Monitor each restaurant
            for restaurant_config in enabled_restaurants:
                await self._monitor_restaurant(client, restaurant_config)

                # Add delay between restaurants to avoid rate limiting
                await random_delay(2.0, 5.0)

        logger.info("Monitoring cycle completed")
        logger.info("=" * 60)

    async def _monitor_restaurant(
        self, client: OmakaseClient, restaurant_config: RestaurantConfig
    ) -> None:
        """
        Monitor a single restaurant for new time slots

        Args:
            client: Authenticated OmakaseClient
            restaurant_config: Restaurant configuration
        """
        try:
            logger.info(f"Checking restaurant: {restaurant_config.name}")

            # Convert RestaurantConfig to Restaurant model
            restaurant = Restaurant(
                name=restaurant_config.name,
                slug=restaurant_config.slug,
                url=restaurant_config.url,
                enabled=restaurant_config.enabled
            )

            # Fetch current time slots
            current_slots = await client.get_time_slots(restaurant.slug)

            if not current_slots:
                logger.info(f"No available time slots for {restaurant.name}")
                # Update cache with empty set
                self.previous_slots[restaurant.slug] = set()
                return

            logger.info(
                f"Found {len(current_slots)} time slots for {restaurant.name}"
            )

            # Convert to set for comparison
            current_slots_set = set(current_slots)

            # Detect new slots
            new_slots = self.detect_new_slots(restaurant, current_slots_set)

            if new_slots:
                logger.info(
                    f"🎉 Detected {len(new_slots)} NEW time slots "
                    f"for {restaurant.name}!"
                )

                # Log details of new slots
                for slot in sorted(new_slots, key=lambda s: (s.date, s.time)):
                    price_str = f"¥{slot.price:,}" if slot.price else "N/A"
                    logger.info(f"  - {slot.date} {slot.time} ({price_str})")

                # Send notification
                await self._send_notification(restaurant, list(new_slots))
            else:
                logger.info(f"No new time slots for {restaurant.name}")

        except Exception as e:
            logger.error(
                f"Error monitoring restaurant {restaurant_config.name}: {e}",
                exc_info=True
            )

    def detect_new_slots(
        self, restaurant: Restaurant, current_slots: Set[TimeSlot]
    ) -> Set[TimeSlot]:
        """
        Detect newly available time slots

        Args:
            restaurant: Restaurant object
            current_slots: Set of currently available time slots

        Returns:
            Set of newly detected time slots
        """
        previous = self.previous_slots.get(restaurant.slug, set())
        new_slots = current_slots - previous

        # Update cache
        self.previous_slots[restaurant.slug] = current_slots

        return new_slots

    async def _send_notification(
        self, restaurant: Restaurant, new_slots: list[TimeSlot]
    ) -> None:
        """
        Send email notification about new time slots

        Args:
            restaurant: Restaurant object
            new_slots: List of new time slots
        """
        try:
            notification = NotificationData(
                restaurant=restaurant,
                new_slots=new_slots,
                timestamp=datetime.now()
            )

            # Send email in a separate thread to avoid blocking
            success = await asyncio.to_thread(
                self.notifier.send_notification,
                self.config.gmail.receiver_email,
                notification
            )

            if success:
                logger.info(
                    f"✉️  Notification sent for {restaurant.name} "
                    f"({len(new_slots)} slots)"
                )
            else:
                logger.error(
                    f"Failed to send notification for {restaurant.name}"
                )

        except Exception as e:
            logger.error(
                f"Error sending notification for {restaurant.name}: {e}",
                exc_info=True
            )
