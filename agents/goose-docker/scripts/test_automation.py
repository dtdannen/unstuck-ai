#!/usr/bin/env python3
import pyautogui
import time
import os


def test_automation():
    """Test basic automation functions"""
    print("Testing automation capabilities...")

    # Test screenshot
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save("/home/goose/workspace/test_screenshot.png")
        print("✅ Screenshot taken successfully")
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")

    # Test mouse movement
    try:
        pyautogui.moveTo(100, 100, duration=1)
        print("✅ Mouse movement works")
    except Exception as e:
        print(f"❌ Mouse movement failed: {e}")

    # Test clicking
    try:
        pyautogui.click(200, 200)
        print("✅ Mouse clicking works")
    except Exception as e:
        print(f"❌ Mouse clicking failed: {e}")


if __name__ == "__main__":
    # Disable PyAutoGUI fail-safe for testing in VNC
    pyautogui.FAILSAFE = False
    test_automation()
