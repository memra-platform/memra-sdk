# File Upload API Specification

## Problem
The remote API tools (PDFProcessor, InvoiceExtractionWorkflow) need access to PDF files, but currently can only access files on the remote server's filesystem. There's no mechanism to upload files from local machines.

## Solution
Implement file upload functionality on the remote API.

## API Endpoint Specification

### POST /upload
Upload a file to the remote API for processing.

**Request:**
```json
{
  "filename": "invoice.pdf",
  "content": "base64_encoded_file_content",
  "content_type": "application/pdf"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "remote_path": "/uploads/invoice.pdf",
    "file_id": "uuid-12345",
    "expires_at": "2025-06-30T23:59:59Z"
  }
}
```

## Implementation Details

1. **File Storage**: Store uploaded files in a temporary directory (e.g., `/tmp/uploads/`)
2. **File Cleanup**: Implement automatic cleanup of files after processing or after a time limit
3. **Security**: Validate file types, size limits, and implement proper authentication
4. **File Naming**: Use unique filenames to prevent conflicts

## Usage in Demo

Once implemented, the demo would:

1. Upload PDF file to remote API
2. Get back a remote file path
3. Pass that remote path to PDFProcessor tool
4. Remote API processes the file and returns extracted data
5. Local MCP bridge writes data to database

## Alternative: Direct File Content

Instead of file upload, modify PDFProcessor to accept file content directly:

```json
{
  "tool_name": "PDFProcessor",
  "hosted_by": "memra",
  "input_data": {
    "file_content": "base64_encoded_pdf_content",
    "filename": "invoice.pdf"
  }
}
```

This would eliminate the need for file upload endpoints. 