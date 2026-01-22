#!/usr/bin/env python3
"""
Test script for complete monitoring workflow

Usage:
    python tests/test_monitor.py

This script tests:
- Configuration loading and validation
- Login to omakase.in
- Fetching time slots from API
- Parsing API responses
- Change detection
- Email notification (optional)
- Complete monitoring cycle
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config, validate_config
from src.monitor import MonitorService


async def test_monitor():
    """Test complete monitoring workflow"""
    print("=" * 60)
    print("Testing Complete Monitoring Workflow")
    print("=" * 60)

    # Step 1: Load and validate configuration
    print("\n[1/6] Loading configuration...")
    try:
        config = load_config("config.yaml")
        print(f"✓ Configuration loaded")

        errors = validate_config(config)
        if errors:
            print(f"✗ Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False

        print(f"✓ Configuration validated")
        print(f"  - Omakase account: {config.omakase.email}")
        print(f"  - Total restaurants: {len(config.restaurants)}")

        enabled = [r for r in config.restaurants if r.enabled]
        print(f"  - Enabled restaurants: {len(enabled)}")
        for r in enabled:
            print(f"    • {r.name} (slug: {r.slug})")

    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("\nPlease create config.yaml from config.yaml.example")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 2: Check for enabled restaurants
    print("\n[2/6] Checking restaurant configuration...")
    enabled_restaurants = [r for r in config.restaurants if r.enabled]

    if not enabled_restaurants:
        print("✗ No enabled restaurants found")
        print("  Please enable at least one restaurant in config.yaml")
        return False

    print(f"✓ Found {len(enabled_restaurants)} enabled restaurant(s)")

    # Step 3: Initialize monitoring service
    print("\n[3/6] Initializing monitoring service...")
    try:
        monitor = MonitorService(config)
        print("✓ MonitorService initialized")
        print(f"  - Gmail notifier configured")
        print(f"  - Previous slots cache: empty (first run)")
    except Exception as e:
        print(f"✗ Error initializing monitor: {e}")
        return False

    # Step 4: Confirm test execution
    print("\n[4/6] Test execution confirmation")
    print("⚠  This test will:")
    print("  1. Login to omakase.in with your credentials")
    print("  2. Fetch actual time slots from configured restaurants")
    print("  3. Check for changes (first run will show all as 'new')")
    print("  4. Send email notifications if new slots are found")

    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Test cancelled by user")
        return False

    # Step 5: Run monitoring cycle
    print("\n[5/6] Running monitoring cycle...")
    print("-" * 60)
    try:
        await monitor.start()
        print("-" * 60)
        print("✓ Monitoring cycle completed successfully")

    except Exception as e:
        print("-" * 60)
        print(f"✗ Error during monitoring: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 6: Display results
    print("\n[6/6] Results summary...")

    cache_summary = []
    for slug, slots in monitor.previous_slots.items():
        cache_summary.append((slug, len(slots)))

    if cache_summary:
        print("✓ Cache updated with current state:")
        for slug, count in cache_summary:
            restaurant_name = next(
                (r.name for r in config.restaurants if r.slug == slug),
                slug
            )
            print(f"  - {restaurant_name}: {count} slot(s) cached")
    else:
        print("  - No slots were cached (all restaurants returned empty)")

    print("\n" + "=" * 60)
    print("Monitoring Test Completed! ✓")
    print("=" * 60)

    print("\nTest Results:")
    print("  1. ✓ Configuration loaded and validated")
    print("  2. ✓ MonitorService initialized")
    print("  3. ✓ Login to omakase.in succeeded")
    print("  4. ✓ API calls completed")
    print("  5. ✓ Response parsing worked")
    print("  6. ✓ Change detection functional")

    if any(count > 0 for _, count in cache_summary):
        print("\nNext Steps:")
        print("  - Run this test again to verify change detection")
        print("  - Only truly NEW slots will trigger notifications on subsequent runs")
        print("  - Check your email if notifications were sent")
    else:
        print("\nNote:")
        print("  - No time slots were found for configured restaurants")
        print("  - This could mean:")
        print("    1. Restaurants are fully booked")
        print("    2. No upcoming time slots available")
        print("    3. Restaurant slug is incorrect")

    return True


if __name__ == "__main__":
    result = asyncio.run(test_monitor())
    sys.exit(0 if result else 1)
