#!/usr/bin/env python3
"""
Omakase Restaurant Reservation Monitor
Main entry point
"""

import asyncio
import logging
from src.monitor import MonitorService
from src.config import load_config


def setup_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('omakase_monitor.log'),
            logging.StreamHandler()
        ]
    )


async def main() -> None:
    """Main execution function"""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting Omakase Monitor...")

        # Load configuration
        config = load_config("config.yaml")
        logger.info(f"Loaded configuration for {len(config.restaurants)} restaurants")

        # Initialize and start monitor service
        monitor = MonitorService(config)
        await monitor.start()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
