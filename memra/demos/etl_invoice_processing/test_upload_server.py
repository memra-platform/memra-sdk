#!/usr/bin/env python3
"""
Local Test Server for File Upload Functionality
This simulates the remote API upload endpoint for testing
"""

import base64
import os
import uuid
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Models
class FileUploadRequest(BaseModel):
    filename: str
    content: str  # base64 encoded
    content_type: str

class FileUploadResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

class ToolExecuteRequest(BaseModel):
    tool_name: str
    hosted_by: str
    input_data: dict

class ToolExecuteResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

# File storage configuration
UPLOAD_DIR = "/tmp/test_uploads"
FILE_EXPIRY_HOURS = 24

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Test Upload Server", version="1.0.0")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(request: FileUploadRequest):
    """Upload a file to the server for processing"""
    try:
        # Validate file type
        if not request.content_type.startswith("application/pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Validate file size (50MB limit)
        try:
            file_content = base64.b64decode(request.content)
            if len(file_content) > 50 * 1024 * 1024:  # 50MB
                raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid base64 content")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(request.filename)[1]
        remote_filename = f"{file_id}{file_extension}"
        remote_path = os.path.join(UPLOAD_DIR, remote_filename)
        
        # Save file
        with open(remote_path, 'wb') as f:
            f.write(file_content)
        
        # Calculate expiry time
        expires_at = datetime.utcnow() + timedelta(hours=FILE_EXPIRY_HOURS)
        
        print(f"📤 Uploaded file: {request.filename} -> {remote_filename}")
        
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

@app.post("/tools/execute", response_model=ToolExecuteResponse)
async def execute_tool(request: ToolExecuteRequest):
    """Execute a tool (simulated PDFProcessor)"""
    try:
        if request.tool_name == "PDFProcessor":
            return await simulate_pdf_processor(request.input_data)
        else:
            return ToolExecuteResponse(
                success=False,
                error=f"Unknown tool: {request.tool_name}"
            )
    except Exception as e:
        return ToolExecuteResponse(
            success=False,
            error=str(e)
        )

async def simulate_pdf_processor(input_data: dict) -> ToolExecuteResponse:
    """Simulate PDF processing"""
    try:
        file_path = input_data.get('file', '')
        
        if not file_path:
            return ToolExecuteResponse(
                success=False,
                error="No file path provided"
            )
        
        # Handle uploaded files
        if file_path.startswith('/uploads/'):
            full_path = os.path.join(UPLOAD_DIR, os.path.basename(file_path))
        else:
            full_path = file_path
        
        if not os.path.exists(full_path):
            return ToolExecuteResponse(
                success=False,
                error=f"PDF file not found: {file_path}"
            )
        
        # Simulate processing (in real implementation, this would use vision model)
        print(f"🔍 Processing PDF: {file_path}")
        
        # Mock extracted data
        invoice_data = {
            "headerSection": {
                "vendorName": "Test Vendor Corp",
                "subtotal": 1234.56
            },
            "billingDetails": {
                "invoiceNumber": "INV-001",
                "invoiceDate": "2024-01-15"
            },
            "chargesSummary": {
                "document_total": 1395.05,
                "secondary_tax": 160.49,
                "lineItemsBreakdown": [
                    {
                        "description": "Test Product",
                        "quantity": 1,
                        "unit_price": 1234.56,
                        "amount": 1234.56,
                        "main_product": True
                    }
                ]
            }
        }
        
        return ToolExecuteResponse(
            success=True,
            data={
                "file_path": file_path,
                "extracted_data": invoice_data
            }
        )
        
    except Exception as e:
        return ToolExecuteResponse(
            success=False,
            error=str(e)
        )

@app.get("/tools/discover")
async def discover_tools():
    """Discover available tools"""
    return {
        "tools": [
            {
                "name": "PDFProcessor",
                "hosted_by": "memra",
                "description": "Process PDF files and extract content"
            },
            {
                "name": "InvoiceExtractionWorkflow",
                "hosted_by": "memra", 
                "description": "Extract structured data from invoices"
            }
        ]
    }

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
                        print(f"🧹 Cleaned up expired file: {filename}")
                    except Exception as e:
                        print(f"Failed to clean up {filename}: {e}")
                        
        except Exception as e:
            print(f"File cleanup error: {e}")
            
        await asyncio.sleep(3600)  # Run every hour

@app.on_event("startup")
async def start_cleanup():
    asyncio.create_task(cleanup_expired_files())

if __name__ == "__main__":
    print("🚀 Starting Test Upload Server...")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 