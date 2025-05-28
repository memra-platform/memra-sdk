from typing import Dict, Any
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class FileReader:
    """Tool for reading files from the filesystem"""
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file and return its contents"""
        logger.info(f"Reading file: {file_path}")
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            with open(path, 'r') as f:
                content = f.read()
                
            # Try to parse as JSON if it's a .json file
            if path.suffix.lower() == '.json':
                try:
                    parsed_content = json.loads(content)
                    return {
                        "success": True,
                        "content": parsed_content,
                        "raw_content": content
                    }
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Invalid JSON: {str(e)}"
                    }
            
            return {
                "success": True,
                "content": content
            }
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 