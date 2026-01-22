"""
HTML and JSON parser for omakase.in responses
"""

import logging
from datetime import datetime
from src.models import TimeSlot

logger = logging.getLogger(__name__)


class OmakaseParser:
    """Parser for omakase.in API responses"""

    @staticmethod
    def parse_time_slots(api_response: dict | list) -> list[TimeSlot]:
        """
        Parse time slots from API response

        The API response structure may vary. This parser attempts to handle
        common formats. Enable DEBUG logging to see the actual response structure.

        Expected formats:
        1. List of slot objects: [{"date": "2026-02-01", "time": "19:00", ...}]
        2. Grouped by date: {"2026-02-01": [{"time": "19:00", ...}]}
        3. Nested structure: {"data": [...], "slots": [...]}

        Args:
            api_response: JSON response from API (dict or list)

        Returns:
            List of TimeSlot objects
        """
        if not api_response:
            logger.info("API response is empty - no time slots available")
            return []

        logger.debug(f"Parsing API response type: {type(api_response)}")
        logger.debug(f"API response keys: {api_response.keys() if isinstance(api_response, dict) else 'N/A'}")

        try:
            # Case 1: Response is a list
            if isinstance(api_response, list):
                return OmakaseParser._parse_slot_list(api_response)

            # Case 2: Response is a dict
            if isinstance(api_response, dict):
                # Try common key names for slot data
                for key in ['slots', 'data', 'time_slots', 'availability', 'online_stock_groups']:
                    if key in api_response:
                        data = api_response[key]
                        if isinstance(data, list):
                            return OmakaseParser._parse_slot_list(data)
                        elif isinstance(data, dict):
                            return OmakaseParser._parse_grouped_slots(data)

                # If no known key found, try to parse the dict directly
                return OmakaseParser._parse_grouped_slots(api_response)

            logger.warning(f"Unexpected API response type: {type(api_response)}")
            return []

        except Exception as e:
            logger.error(f"Error parsing API response: {e}", exc_info=True)
            logger.debug(f"Failed response content: {api_response}")
            return []

    @staticmethod
    def _parse_slot_list(slots: list) -> list[TimeSlot]:
        """
        Parse a list of time slot objects

        Expected format:
        [
            {"date": "2026-02-01", "time": "19:00", "price": 15000, ...},
            {"date": "2026-02-01", "time": "21:00", "price": 15000, ...}
        ]
        """
        parsed_slots = []

        for slot_data in slots:
            if not isinstance(slot_data, dict):
                logger.warning(f"Skipping non-dict slot: {slot_data}")
                continue

            try:
                slot = OmakaseParser._parse_single_slot(slot_data)
                if slot:
                    parsed_slots.append(slot)
            except Exception as e:
                logger.warning(f"Failed to parse slot {slot_data}: {e}")

        logger.info(f"Parsed {len(parsed_slots)} time slots from list")
        return parsed_slots

    @staticmethod
    def _parse_grouped_slots(grouped: dict) -> list[TimeSlot]:
        """
        Parse slots grouped by date

        Expected format:
        {
            "2026-02-01": [
                {"time": "19:00", "price": 15000, ...},
                {"time": "21:00", "price": 15000, ...}
            ],
            "2026-02-02": [...]
        }
        """
        parsed_slots = []

        for date_key, slots_data in grouped.items():
            # Try to validate if key looks like a date
            if not OmakaseParser._looks_like_date(date_key):
                logger.debug(f"Skipping non-date key: {date_key}")
                continue

            if not isinstance(slots_data, list):
                logger.warning(f"Expected list for date {date_key}, got {type(slots_data)}")
                continue

            for slot_data in slots_data:
                if not isinstance(slot_data, dict):
                    continue

                try:
                    # Add date to slot data if not present
                    if 'date' not in slot_data:
                        slot_data['date'] = date_key

                    slot = OmakaseParser._parse_single_slot(slot_data)
                    if slot:
                        parsed_slots.append(slot)
                except Exception as e:
                    logger.warning(f"Failed to parse slot for {date_key}: {e}")

        logger.info(f"Parsed {len(parsed_slots)} time slots from grouped data")
        return parsed_slots

    @staticmethod
    def _parse_single_slot(slot_data: dict) -> TimeSlot | None:
        """
        Parse a single time slot object

        Required fields: date, time
        Optional fields: price, booking_url, available_seats, seats, url, link

        Args:
            slot_data: Dictionary containing slot information

        Returns:
            TimeSlot object or None if required fields are missing
        """
        # Extract date - try multiple possible keys
        date = None
        for date_key in ['date', 'day', 'booking_date', 'reservation_date']:
            if date_key in slot_data:
                date = str(slot_data[date_key])
                break

        # Extract time - try multiple possible keys
        time = None
        for time_key in ['time', 'start_time', 'booking_time', 'reservation_time']:
            if time_key in slot_data:
                time = str(slot_data[time_key])
                break

        if not date or not time:
            logger.debug(f"Missing required fields (date/time) in slot: {slot_data}")
            return None

        # Normalize date format (YYYY-MM-DD)
        date = OmakaseParser._normalize_date(date)

        # Normalize time format (HH:MM)
        time = OmakaseParser._normalize_time(time)

        # Extract price - try multiple possible keys
        price = None
        for price_key in ['price', 'amount', 'cost', 'price_amount']:
            if price_key in slot_data:
                try:
                    price = int(slot_data[price_key])
                    break
                except (ValueError, TypeError):
                    pass

        # Extract booking URL - try multiple possible keys
        booking_url = None
        for url_key in ['booking_url', 'url', 'link', 'reservation_url', 'booking_link']:
            if url_key in slot_data:
                booking_url = str(slot_data[url_key])
                break

        # Extract available seats - try multiple possible keys
        available_seats = None
        for seats_key in ['available_seats', 'seats', 'capacity', 'available']:
            if seats_key in slot_data:
                try:
                    available_seats = int(slot_data[seats_key])
                    break
                except (ValueError, TypeError):
                    pass

        return TimeSlot(
            date=date,
            time=time,
            price=price,
            booking_url=booking_url,
            available_seats=available_seats
        )

    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """
        Normalize date to YYYY-MM-DD format

        Accepts: "2026-02-01", "2026/02/01", "20260201", etc.
        """
        # Remove common separators and try to parse
        date_str = date_str.strip()

        # Already in correct format
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str

        # Try common formats
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%d-%m-%Y', '%d/%m/%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # If all fails, return as-is and log warning
        logger.warning(f"Could not normalize date: {date_str}")
        return date_str

    @staticmethod
    def _normalize_time(time_str: str) -> str:
        """
        Normalize time to HH:MM format

        Accepts: "19:00", "19:00:00", "1900", "7:00 PM", etc.
        """
        time_str = time_str.strip()

        # Already in correct format
        if len(time_str) == 5 and time_str[2] == ':':
            return time_str

        # Remove seconds if present (HH:MM:SS -> HH:MM)
        if len(time_str) == 8 and time_str[2] == ':' and time_str[5] == ':':
            return time_str[:5]

        # Try to parse various formats
        for fmt in ['%H:%M', '%H:%M:%S', '%I:%M %p', '%H%M']:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.strftime('%H:%M')
            except ValueError:
                continue

        # If all fails, return as-is and log warning
        logger.warning(f"Could not normalize time: {time_str}")
        return time_str

    @staticmethod
    def _looks_like_date(s: str) -> bool:
        """Check if a string looks like a date"""
        # Simple heuristic: contains digits and common date separators
        if not isinstance(s, str):
            return False

        # Must contain at least some digits
        if not any(c.isdigit() for c in s):
            return False

        # Common date patterns
        date_patterns = ['-', '/', '年', '月', '日']
        return any(sep in s for sep in date_patterns) or s.isdigit()


def debug_api_response(api_response: dict | list) -> None:
    """
    Helper function to debug API response structure

    Call this function with the raw API response to see its structure
    and help identify the correct parsing strategy.
    """
    import json

    print("=" * 60)
    print("API Response Debug Information")
    print("=" * 60)
    print(f"Type: {type(api_response)}")

    if isinstance(api_response, dict):
        print(f"Keys: {list(api_response.keys())}")
        print("\nFirst level structure:")
        for key, value in api_response.items():
            print(f"  {key}: {type(value)}")
            if isinstance(value, (list, dict)) and value:
                if isinstance(value, list):
                    print(f"    -> List with {len(value)} items")
                    if value:
                        print(f"    -> First item type: {type(value[0])}")
                elif isinstance(value, dict):
                    print(f"    -> Dict with keys: {list(value.keys())[:5]}")

    elif isinstance(api_response, list):
        print(f"List with {len(api_response)} items")
        if api_response:
            print(f"First item type: {type(api_response[0])}")
            if isinstance(api_response[0], dict):
                print(f"First item keys: {list(api_response[0].keys())}")

    print("\nFull response (formatted):")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    print("=" * 60)
