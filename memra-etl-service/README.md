# Memra ETL API Service

A standalone ETL (Extract, Transform, Load) API service for invoice processing, completely separate from the chatbot functionality.

## Features

- **PDF Processing**: Extract invoice data using Fireworks AI vision model
- **Data Validation**: Validate extracted data against schema
- **Database Integration**: Insert validated data into PostgreSQL
- **Standalone Service**: No interference with chatbot functionality

## API Endpoints

### Health Check
```
GET /health
```

### List Tools
```
GET /tools
```

### Execute Tool
```
POST /tools/execute
Content-Type: application/json

{
  "tool_name": "PDFProcessor|DataValidator|PostgresInsert",
  "input_data": {
    // Tool-specific input data
  }
}
```

## Available Tools

1. **PDFProcessor**: Process PDF files and extract invoice data using vision model
2. **DataValidator**: Validate extracted invoice data against schema  
3. **PostgresInsert**: Insert validated invoice data into PostgreSQL database

## Environment Variables

- `ETL_POSTGRES_URL`: PostgreSQL connection string
- `HUGGINGFACE_API_KEY`: Fireworks AI API key
- `PORT`: Server port (default: 8080)

## Deployment

This service is deployed as a separate Fly.io app (`memra-etl-api`) to ensure complete isolation from the chatbot service.

## Usage

The ETL demo can be configured to use this service instead of the chatbot server by updating the API URL in the demo configuration. 