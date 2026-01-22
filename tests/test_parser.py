#!/usr/bin/env python3
"""
Test script for API response parser

Usage:
    python tests/test_parser.py

This script tests:
- Parser with different API response formats
- Date/time normalization
- Field extraction
- Error handling
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import OmakaseParser


def test_parser():
    """Test parser with various API response formats"""
    print("=" * 60)
    print("Testing API Response Parser")
    print("=" * 60)

    # Test Case 1: List format
    print("\n[Test 1] List format")
    response1 = [
        {
            "date": "2026-02-15",
            "time": "19:00",
            "price": 15000,
            "booking_url": "https://omakase.in/ja/r/test/book/1",
            "available_seats": 2
        },
        {
            "date": "2026-02-15",
            "time": "21:00",
            "price": 18000,
            "booking_url": "https://omakase.in/ja/r/test/book/2",
            "available_seats": 1
        }
    ]

    slots1 = OmakaseParser.parse_time_slots(response1)
    print(f"  - Input: List with {len(response1)} items")
    print(f"  - Parsed: {len(slots1)} time slots")
    for slot in slots1:
        print(f"    • {slot.date} {slot.time} - ¥{slot.price:,} ({slot.available_seats} seats)")
    assert len(slots1) == 2, "Should parse 2 slots"
    print("  ✓ Passed")

    # Test Case 2: Grouped by date
    print("\n[Test 2] Grouped by date format")
    response2 = {
        "2026-02-15": [
            {"time": "19:00", "price": 15000},
            {"time": "21:00", "price": 18000}
        ],
        "2026-02-16": [
            {"time": "19:00", "price": 15000}
        ]
    }

    slots2 = OmakaseParser.parse_time_slots(response2)
    print(f"  - Input: Dict with {len(response2)} dates")
    print(f"  - Parsed: {len(slots2)} time slots")
    for slot in slots2:
        print(f"    • {slot.date} {slot.time} - ¥{slot.price:,}")
    assert len(slots2) == 3, "Should parse 3 slots"
    print("  ✓ Passed")

    # Test Case 3: Nested with 'data' key
    print("\n[Test 3] Nested structure with 'data' key")
    response3 = {
        "status": "success",
        "data": [
            {"date": "2026-02-15", "time": "19:00", "price": 15000}
        ]
    }

    slots3 = OmakaseParser.parse_time_slots(response3)
    print(f"  - Input: Nested dict with 'data' key")
    print(f"  - Parsed: {len(slots3)} time slots")
    assert len(slots3) == 1, "Should parse 1 slot"
    print("  ✓ Passed")

    # Test Case 4: Different date/time formats
    print("\n[Test 4] Date/time format normalization")
    response4 = [
        {"date": "2026/02/15", "time": "19:00:00"},  # Different separators
        {"date": "20260215", "time": "1900"},         # No separators
        {"booking_date": "2026-02-16", "start_time": "7:00 PM"}  # Different field names
    ]

    slots4 = OmakaseParser.parse_time_slots(response4)
    print(f"  - Input: Various date/time formats")
    print(f"  - Parsed: {len(slots4)} time slots")
    for slot in slots4:
        print(f"    • {slot.date} {slot.time}")
    assert len(slots4) == 3, "Should parse 3 slots"
    # Check normalization
    assert slots4[0].date == "2026-02-15", "Date should be normalized"
    assert slots4[0].time == "19:00", "Time should be normalized"
    print("  ✓ Passed")

    # Test Case 5: Empty response
    print("\n[Test 5] Empty response")
    response5 = []
    slots5 = OmakaseParser.parse_time_slots(response5)
    print(f"  - Input: Empty list")
    print(f"  - Parsed: {len(slots5)} time slots")
    assert len(slots5) == 0, "Should return empty list"
    print("  ✓ Passed")

    # Test Case 6: Missing required fields
    print("\n[Test 6] Missing required fields")
    response6 = [
        {"date": "2026-02-15"},  # Missing time
        {"time": "19:00"},       # Missing date
        {"price": 15000},        # Missing both
        {"date": "2026-02-15", "time": "19:00", "price": 15000}  # Valid
    ]

    slots6 = OmakaseParser.parse_time_slots(response6)
    print(f"  - Input: 4 items (1 valid, 3 invalid)")
    print(f"  - Parsed: {len(slots6)} time slots")
    assert len(slots6) == 1, "Should only parse valid slot"
    print("  ✓ Passed")

    # Test Case 7: Alternative field names
    print("\n[Test 7] Alternative field names")
    response7 = [
        {
            "booking_date": "2026-02-15",
            "start_time": "19:00",
            "amount": 15000,
            "reservation_url": "https://example.com",
            "seats": 2
        }
    ]

    slots7 = OmakaseParser.parse_time_slots(response7)
    print(f"  - Input: Alternative field names")
    print(f"  - Parsed: {len(slots7)} time slots")
    assert len(slots7) == 1, "Should parse with alternative names"
    slot = slots7[0]
    assert slot.price == 15000, "Should extract price from 'amount'"
    assert slot.booking_url == "https://example.com", "Should extract URL"
    assert slot.available_seats == 2, "Should extract seats"
    print(f"    • All fields extracted correctly")
    print("  ✓ Passed")

    print("\n" + "=" * 60)
    print("All Parser Tests Passed! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        result = test_parser()
        sys.exit(0 if result else 1)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
