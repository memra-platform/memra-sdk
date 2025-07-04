# Remote API File Upload Implementation Guide

## Overview
The remote API at api.memra.co needs file upload functionality to process PDF files from local machines. This guide provides the implementation details.

## Current API Structure
Based on the API responses, the server appears to be using FastAPI with these endpoints:
- `GET /health` - Health check
- `GET /tools/discover` - Discover available tools  
- `POST /tools/execute` - Execute workflow tools

## Implementation Plan

### 1. Add Upload Endpoint

Add this endpoint to your FastAPI server:

```python
import base64
import os
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# Models
class FileUploadRequest(BaseModel):
    filename: str
    content: str  # base64 encoded
    content_type: str

class FileUploadResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

# File storage configuration
UPLOAD_DIR = "/tmp/uploads"
FILE_EXPIRY_HOURS = 24

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(request: FileUploadRequest):
    """Upload a file to the server for processing"""
    try:
        # Validate file type
        if not request.content_type.startswith("application/pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(request.filename)[1]
        remote_filename = f"{file_id}{file_extension}"
        remote_path = os.path.join(UPLOAD_DIR, remote_filename)
        
        # Decode and save file
        try:
            file_content = base64.b64decode(request.content)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 content")
        
        with open(remote_path, 'wb') as f:
            f.write(file_content)
        
        # Calculate expiry time
        expires_at = datetime.utcnow() + timedelta(hours=FILE_EXPIRY_HOURS)
        
        return FileUploadResponse(
            success=True,
            data={
                "remote_path": f"/uploads/{remote_filename}",
                "file_id": file_id,
                "expires_at": expires_at.isoformat(),
                "original_filename": request.filename
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return FileUploadResponse(
            success=False,
            error=f"Upload failed: {str(e)}"
        )
```

### 2. Add File Cleanup

Add a background task to clean up expired files:

```python
import asyncio
from datetime import datetime

async def cleanup_expired_files():
    """Remove files older than FILE_EXPIRY_HOURS"""
    while True:
        try:
            current_time = datetime.utcnow()
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if current_time - file_time > timedelta(hours=FILE_EXPIRY_HOURS):
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up expired file: {filename}")
                    except Exception as e:
                        print(f"Failed to clean up {filename}: {e}")
                        
        except Exception as e:
            print(f"File cleanup error: {e}")
            
        await asyncio.sleep(3600)  # Run every hour

# Start cleanup task
@app.on_event("startup")
async def start_cleanup():
    asyncio.create_task(cleanup_expired_files())
```

### 3. Update PDFProcessor Tool

Modify the PDFProcessor tool to handle uploaded files:

```python
async def pdf_processor_tool(input_data: dict) -> dict:
    """Process PDF file and extract invoice data"""
    try:
        file_path = input_data.get('file', '')
        
        if not file_path:
            return {
                "success": False,
                "error": "No file path provided"
            }
        
        # Handle uploaded files
        if file_path.startswith('/uploads/'):
            full_path = os.path.join(UPLOAD_DIR, os.path.basename(file_path))
        else:
            full_path = file_path
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"PDF file not found: {file_path}"
            }
        
        # Process the PDF file
        # ... your existing PDF processing logic ...
        
        return {
            "success": True,
            "data": {
                "file_path": file_path,
                "extracted_data": invoice_data
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 4. Security Considerations

1. **File Size Limits**: Add maximum file size validation
2. **File Type Validation**: Only allow PDF files
3. **Rate Limiting**: Prevent abuse
4. **Authentication**: Ensure uploads require valid API key

```python
# Add to upload endpoint
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Validate file size
if len(file_content) > MAX_FILE_SIZE:
    raise HTTPException(status_code=400, detail="File too large (max 50MB)")
```

## Testing the Implementation

### 1. Test Upload Endpoint

```bash
# Test file upload
curl -X POST https://api.memra.co/upload \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.pdf",
    "content": "JVBERi0xLjQKJcOkw7zDtsO...",
    "content_type": "application/pdf"
  }'
```

### 2. Test PDFProcessor with Uploaded File

```bash
# Test PDF processing with uploaded file
curl -X POST https://api.memra.co/tools/execute \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "PDFProcessor",
    "hosted_by": "memra",
    "input_data": {
      "file": "/uploads/uuid-12345.pdf"
    }
  }'
```

## Deployment Notes

1. **Storage**: Use persistent storage for production (not /tmp)
2. **Monitoring**: Add logging for upload/processing events
3. **Scaling**: Consider using cloud storage (S3, etc.) for high-volume usage
4. **Backup**: Implement file backup if needed

## Alternative: Direct File Content

Instead of file upload, you could modify PDFProcessor to accept file content directly:

```python
async def pdf_processor_tool(input_data: dict) -> dict:
    """Process PDF file content directly"""
    try:
        file_content = input_data.get('file_content')
        filename = input_data.get('filename', 'unknown.pdf')
        
        if not file_content:
            return {
                "success": False,
                "error": "No file content provided"
            }
        
        # Decode base64 content
        try:
            pdf_content = base64.b64decode(file_content)
        except Exception:
            return {
                "success": False,
                "error": "Invalid base64 content"
            }
        
        # Process PDF content directly
        # ... your PDF processing logic ...
        
        return {
            "success": True,
            "data": {
                "filename": filename,
                "extracted_data": invoice_data
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

This approach eliminates the need for file upload endpoints entirely. 