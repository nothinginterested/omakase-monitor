"""
Utility functions
"""

import asyncio
import random
from functools import wraps
import logging

logger = logging.getLogger(__name__)


async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """Add random delay to avoid rate limiting"""
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Random delay: {delay:.2f}s")
    await asyncio.sleep(delay)


def retry_on_failure(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator for exponential backoff retry"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator
