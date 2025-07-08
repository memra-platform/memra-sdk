#!/usr/bin/env python3
"""Test API connectivity"""

import os
import requests
import json

def test_api():
    # Test remote API
    print("Testing remote API...")
    try:
        response = requests.get("https://api.memra.co/health", timeout=10)
        print(f"Remote API Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Remote API Error: {e}")
    
    # Test local API
    print("\nTesting local API...")
    try:
        response = requests.get("http://127.0.0.1:8081/health", timeout=5)
        print(f"Local API Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Local API Error: {e}")

if __name__ == "__main__":
    test_api() 