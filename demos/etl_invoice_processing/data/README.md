# Demo Data Files

This directory contains sample data files for the ETL Invoice Processing demo.

## 📁 Directory Structure

```
data/
├── invoices/           # PDF invoice files for processing
│   ├── invoice_001.pdf
│   ├── invoice_002.pdf
│   └── ...
└── README.md          # This file
```

## 📄 Invoice Files

The `invoices/` directory contains sample PDF invoice files that demonstrate:

- **Various invoice formats** from different vendors
- **Different data structures** (line items, totals, tax calculations)
- **Real-world scenarios** (missing data, edge cases)
- **Multiple currencies** and payment terms

## 🚀 Using the Demo Data

### Option 1: Auto-Discovery (Recommended)
The demo will automatically scan the `invoices/` directory:

```python
# The demo will find and process all PDF files
python etl_invoice_demo.py
```

### Option 2: Specific File Processing
Process a specific invoice file:

```python
# Update the demo to process a specific file
input_data = {
    "invoice_file": "data/invoices/invoice_001.pdf",
    "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db"
}
```

### Option 3: External File Processing
Copy files from external locations:

```python
# The demo can copy files from Downloads or other locations
input_data = {
    "source_path": "~/Downloads/new_invoice.pdf",
    "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db"
}
```

## 📊 Expected Data Structure

Each invoice file should contain:

- **Vendor Information**: Company name, address, contact details
- **Invoice Details**: Invoice number, date, due date
- **Line Items**: Description, quantity, unit price, total
- **Totals**: Subtotal, tax, shipping, grand total
- **Payment Terms**: Due date, payment methods

## 🔧 Customizing the Data

### Adding New Invoice Files
1. Place new PDF files in the `invoices/` directory
2. Ensure they follow the expected invoice format
3. Test with the demo to verify processing

### Modifying Existing Files
- Files are processed using AI vision models
- No specific format requirements
- The system adapts to different invoice layouts

## 📈 Demo Scenarios

The included files demonstrate:

| Scenario | Description |
|----------|-------------|
| **Standard Invoice** | Typical business invoice with line items |
| **Complex Invoice** | Multiple pages, detailed line items |
| **Simple Invoice** | Basic invoice with minimal details |
| **International** | Different currencies and formats |
| **Edge Cases** | Missing data, unusual formats |

## 🚨 Important Notes

- **File Size**: Each file is approximately 1MB
- **Total Size**: ~20MB for all demo files
- **Git LFS**: Not required for these file sizes
- **Version Control**: Files are tracked in Git for demo consistency

## 🔄 Updating Demo Data

When adding new invoice files:

1. **Test locally** first
2. **Verify processing** with the demo
3. **Update this README** if adding new scenarios
4. **Commit changes** with descriptive messages

## 📚 Related Documentation

- [ETL Demo Guide](../README.md)
- [Database Schema](../../../docs/database_schema.sql)
- [Sample Data](../../../docs/sample_data.sql)
- [Quick Start Guide](../../../QUICK_START.md) 