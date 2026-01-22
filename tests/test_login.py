#!/usr/bin/env python3
"""
Test script for omakase.in login functionality

Usage:
    python tests/test_login.py

This script tests:
- Configuration loading
- OmakaseClient initialization
- Login to omakase.in
- Cookie persistence
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config, validate_config
from src.omakase_client import OmakaseClient


async def test_login():
    """Test login functionality"""
    print("=" * 60)
    print("Testing omakase.in Login")
    print("=" * 60)

    # Step 1: Load configuration
    print("\n[1/5] Loading configuration...")
    try:
        config = load_config("config.yaml")
        print(f"✓ Configuration loaded successfully")
        print(f"  - Omakase email: {config.omakase.email}")
        print(f"  - Restaurants: {len(config.restaurants)}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("\nPlease create config.yaml from config.yaml.example")
        return False
    except ValueError as e:
        print(f"✗ Configuration validation failed:")
        print(f"  {e}")
        return False

    # Step 2: Validate configuration
    print("\n[2/5] Validating configuration...")
    errors = validate_config(config)
    if errors:
        print(f"✗ Configuration has errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    print("✓ Configuration is valid")

    # Step 3: Check for existing cookies
    print("\n[3/5] Checking for existing cookies...")
    cookies_file = Path("cookies.json")
    if cookies_file.exists():
        print(f"✓ Found existing cookies file")
        print(f"  - Location: {cookies_file}")
    else:
        print(f"  - No existing cookies found (will create after login)")

    # Step 4: Initialize client and attempt login
    print("\n[4/5] Attempting login to omakase.in...")
    try:
        async with OmakaseClient() as client:
            success = await client.login(
                config.omakase.email,
                config.omakase.password
            )

            if success:
                print("✓ Login successful!")
                print(f"  - Session established")
                print(f"  - Cookies saved to: cookies.json")
            else:
                print("✗ Login failed")
                print("  - Check your email/password in config.yaml")
                print("  - Check if omakase.in is accessible")
                return False

    except Exception as e:
        print(f"✗ Error during login: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 5: Test cookie persistence
    print("\n[5/5] Testing cookie persistence...")
    try:
        async with OmakaseClient() as client:
            # This should use saved cookies
            success = await client.login(
                config.omakase.email,
                config.omakase.password
            )

            if success and client.is_logged_in:
                print("✓ Cookie persistence working")
                print("  - Reused existing session")
            else:
                print("⚠ Cookie persistence may have issues")

    except Exception as e:
        print(f"⚠ Error testing cookie persistence: {e}")

    print("\n" + "=" * 60)
    print("Login Test Completed Successfully! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = asyncio.run(test_login())
    sys.exit(0 if result else 1)
