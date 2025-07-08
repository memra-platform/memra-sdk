#!/usr/bin/env python3
"""
Debug script to test MCP bridge connection
"""

import httpx
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mcp_bridge():
    """Test MCP bridge connection using httpx"""
    
    bridge_url = "http://localhost:8081"
    bridge_secret = "test-secret-for-development"
    
    # Prepare request
    payload = {
        "tool_name": "SQLExecutor",
        "input_data": {
            "sql_query": "SELECT COUNT(*) as row_count FROM invoices"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Bridge-Secret": bridge_secret
    }
    
    logger.info(f"Testing MCP bridge at {bridge_url}")
    logger.info(f"Payload: {json.dumps(payload, indent=2)}")
    logger.info(f"Headers: {headers}")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            logger.info("Making HTTP request...")
            response = client.post(f"{bridge_url}/execute_tool", json=payload, headers=headers)
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Success! Result: {json.dumps(result, indent=2)}")
                return True
            else:
                logger.error(f"HTTP error: {response.status_code}")
                logger.error(f"Response text: {response.text}")
                return False
                
    except httpx.TimeoutException:
        logger.error("Request timed out")
        return False
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mcp_bridge()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}") 