#!/usr/bin/env python3
"""
Test script for email notification

Usage:
    python tests/test_email.py

This script tests:
- Gmail SMTP connection
- Email template rendering
- Email sending
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.notifier import GmailNotifier
from src.models import Restaurant, TimeSlot, NotificationData


def test_email():
    """Test email notification functionality"""
    print("=" * 60)
    print("Testing Email Notification")
    print("=" * 60)

    # Step 1: Load configuration
    print("\n[1/3] Loading configuration...")
    try:
        config = load_config("config.yaml")
        print(f"✓ Configuration loaded")
        print(f"  - Sender: {config.gmail.sender_email}")
        print(f"  - Receiver: {config.gmail.receiver_email}")
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False

    # Step 2: Create test data
    print("\n[2/3] Creating test notification data...")

    # Create a test restaurant
    restaurant = Restaurant(
        name="Test Restaurant (寿司テスト)",
        slug="test123",
        url="https://omakase.in/ja/r/test123",
        enabled=True
    )

    # Create test time slots
    test_slots = [
        TimeSlot(
            date="2026-02-15",
            time="19:00",
            price=15000,
            booking_url="https://omakase.in/ja/r/test123/book/1",
            available_seats=2
        ),
        TimeSlot(
            date="2026-02-15",
            time="21:00",
            price=18000,
            booking_url="https://omakase.in/ja/r/test123/book/2",
            available_seats=1
        ),
        TimeSlot(
            date="2026-02-16",
            time="19:00",
            price=15000,
            booking_url=None,  # Test without booking URL
            available_seats=None  # Test without seat count
        )
    ]

    notification = NotificationData(
        restaurant=restaurant,
        new_slots=test_slots,
        timestamp=datetime.now()
    )

    print(f"✓ Test data created")
    print(f"  - Restaurant: {restaurant.name}")
    print(f"  - New slots: {len(test_slots)}")
    for slot in test_slots:
        price_str = f"¥{slot.price:,}" if slot.price else "N/A"
        print(f"    • {slot.date} {slot.time} - {price_str}")

    # Step 3: Send test email
    print("\n[3/3] Sending test email...")
    print("⚠  This will send a real email to the configured receiver!")

    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Test cancelled by user")
        return False

    try:
        notifier = GmailNotifier(
            smtp_server=config.gmail.smtp_server,
            smtp_port=config.gmail.smtp_port,
            sender_email=config.gmail.sender_email,
            app_password=config.gmail.app_password
        )

        success = notifier.send_notification(
            config.gmail.receiver_email,
            notification
        )

        if success:
            print("✓ Email sent successfully!")
            print(f"  - Check inbox: {config.gmail.receiver_email}")
            print(f"  - Subject: [Omakase] {restaurant.name} - New Reservations Available")
            print(f"\nEmail should contain:")
            print(f"  - Restaurant name (with Japanese characters)")
            print(f"  - 3 time slots in a table")
            print(f"  - Properly formatted prices")
            print(f"  - Links to booking pages")
            print(f"  - HTML formatting")
        else:
            print("✗ Failed to send email")
            print("  - Check your Gmail App Password in .env")
            print("  - Verify sender email has 2-Step Verification enabled")
            print("  - Check logs for detailed error messages")
            return False

    except Exception as e:
        print(f"✗ Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("Email Test Completed! ✓")
    print("=" * 60)
    print("\nPlease verify:")
    print("  1. Email was received")
    print("  2. HTML formatting is correct")
    print("  3. All 3 time slots are displayed")
    print("  4. Prices are formatted correctly (¥15,000)")
    print("  5. Links are clickable")
    print("  6. Japanese characters display correctly")

    return True


if __name__ == "__main__":
    result = test_email()
    sys.exit(0 if result else 1)
