# File Upload Testing Guide

This guide helps you test the file upload functionality before implementing it on the remote API.

## Overview

The ETL demo workflow needs to upload PDF files to the remote API for processing. Since the remote API doesn't have the upload endpoint yet, we've created a local test server to verify the functionality works.

## Quick Start

### 1. Install Dependencies

```bash
# Install test server dependencies
pip install -r requirements_test_server.txt

# Or install individually
pip install fastapi uvicorn pydantic requests
```

### 2. Start the Test Server

```bash
# Start the test upload server
python3 test_upload_server.py
```

You should see:
```
🚀 Starting Test Upload Server...
📁 Upload directory: /tmp/test_uploads
🌐 Server will be available at: http://localhost:8000
📚 API docs available at: http://localhost:8000/docs
```

### 3. Test the Upload Functionality

In a new terminal:

```bash
# Run the upload test
python3 test_upload_functionality.py
```

This will:
- Check server health
- Discover available tools
- Create a test PDF file
- Upload it to the server
- Process it with the PDFProcessor tool
- Show extracted data

### 4. Test the Full ETL Demo

```bash
# Run the ETL demo with upload functionality
python3 etl_invoice_demo.py
```

## API Endpoints

The test server provides these endpoints:

### Health Check
```
GET /health
```

### File Upload
```
POST /upload
Content-Type: application/json

{
  "filename": "invoice.pdf",
  "content": "base64_encoded_content",
  "content_type": "application/pdf"
}
```

### Tool Discovery
```
GET /tools/discover
```

### Tool Execution
```
POST /tools/execute
Content-Type: application/json

{
  "tool_name": "PDFProcessor",
  "hosted_by": "memra",
  "input_data": {
    "file": "/uploads/uuid-12345.pdf"
  }
}
```

## Implementation Details

### File Storage
- Files are stored in `/tmp/test_uploads/`
- Each file gets a unique UUID filename
- Files expire after 24 hours (automatic cleanup)

### Security Features
- File type validation (PDF only)
- File size limits (50MB max)
- Base64 content validation

### Error Handling
- Invalid file types return 400 error
- File too large returns 400 error
- Invalid base64 content returns 400 error
- File not found returns error in tool execution

## Testing with Real PDFs

To test with actual PDF files:

1. Place your PDF files in `data/invoices/`
2. Run the ETL demo:
   ```bash
   python3 etl_invoice_demo.py
   ```

The demo will:
- Upload each PDF to the test server
- Process them with the PDFProcessor tool
- Extract invoice data
- Store results in the database

## Switching to Remote API

When you're ready to implement on the remote API:

1. **Update the API URL** in `etl_invoice_demo.py`:
   ```python
   def upload_file_to_api(file_path: str, api_url: str = "https://api.memra.co") -> str:
   ```

2. **Add API key authentication**:
   ```python
   headers={
       "X-API-Key": os.getenv('MEMRA_API_KEY'),
       "Content-Type": "application/json"
   }
   ```

3. **Implement the upload endpoint** on the remote API using the specification in `REMOTE_API_UPLOAD_IMPLEMENTATION.md`

## Troubleshooting

### Server Won't Start
- Check if port 8000 is available
- Install dependencies: `pip install fastapi uvicorn`
- Check Python version (3.7+ required)

### Upload Fails
- Check server is running on localhost:8000
- Verify file is a valid PDF
- Check file size (max 50MB)
- Look at server logs for error details

### Processing Fails
- Check if uploaded file exists in `/tmp/test_uploads/`
- Verify file path is correct
- Check server logs for processing errors

### Database Issues
- Make sure PostgreSQL is running
- Check MCP bridge is healthy
- Verify database connection string

## Next Steps

1. **Test with the local server** to verify functionality
2. **Implement upload endpoint** on remote API using the implementation guide
3. **Update demo** to use remote API
4. **Test with real PDF files** in production
5. **Monitor file cleanup** and storage usage

## Files

- `test_upload_server.py` - Local test server
- `test_upload_functionality.py` - Upload testing script
- `REMOTE_API_UPLOAD_IMPLEMENTATION.md` - Implementation guide for remote API
- `requirements_test_server.txt` - Test server dependencies
- `etl_invoice_demo.py` - Updated demo with upload functionality 