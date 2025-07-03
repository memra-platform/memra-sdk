#!/usr/bin/env python3
"""
Setup Demo Data Script
Helps users set up invoice files for the ETL demo
"""

import os
import shutil
import sys
from pathlib import Path

def create_demo_structure():
    """Create the demo data directory structure"""
    
    # Define paths
    demo_dir = Path(__file__).parent
    data_dir = demo_dir / "data"
    invoices_dir = data_dir / "invoices"
    
    # Create directories
    invoices_dir.mkdir(parents=True, exist_ok=True)
    
    print("📁 Created demo data structure:")
    print(f"  {data_dir}")
    print(f"  {invoices_dir}")
    
    return invoices_dir

def check_existing_files(invoices_dir):
    """Check for existing invoice files"""
    
    pdf_files = list(invoices_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"\n📄 Found {len(pdf_files)} existing invoice files:")
        for pdf_file in pdf_files:
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            print(f"  - {pdf_file.name} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"\n📄 No invoice files found in {invoices_dir}")
        return False

def copy_sample_files(invoices_dir):
    """Copy sample files from external locations if available"""
    
    # Common locations where users might have invoice files
    sample_locations = [
        Path.home() / "Downloads",
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.cwd() / "invoices",  # If they have an invoices folder in current directory
    ]
    
    print("\n🔍 Looking for sample invoice files...")
    
    for location in sample_locations:
        if location.exists():
            pdf_files = list(location.glob("*.pdf"))
            if pdf_files:
                print(f"  Found {len(pdf_files)} PDF files in {location}")
                
                # Copy first few files (up to 5)
                copied = 0
                for pdf_file in pdf_files[:5]:
                    if copied >= 5:
                        break
                    
                    dest_file = invoices_dir / f"invoice_{copied+1:03d}.pdf"
                    try:
                        shutil.copy2(pdf_file, dest_file)
                        size_mb = pdf_file.stat().st_size / (1024 * 1024)
                        print(f"    ✅ Copied {pdf_file.name} -> {dest_file.name} ({size_mb:.1f} MB)")
                        copied += 1
                    except Exception as e:
                        print(f"    ❌ Failed to copy {pdf_file.name}: {e}")
                
                if copied > 0:
                    return True
    
    return False

def create_placeholder_files(invoices_dir):
    """Create placeholder files for testing"""
    
    print("\n📝 Creating placeholder files for testing...")
    
    # Create a simple text file as placeholder
    placeholder_content = """
This is a placeholder file for the ETL Invoice Processing demo.

To use real invoice files:
1. Place your PDF invoice files in this directory
2. Rename them to invoice_001.pdf, invoice_002.pdf, etc.
3. Run the demo: python etl_invoice_demo.py

The demo will automatically discover and process all PDF files in this directory.
"""
    
    placeholder_file = invoices_dir / "README.txt"
    with open(placeholder_file, 'w') as f:
        f.write(placeholder_content)
    
    print(f"  ✅ Created {placeholder_file}")
    return False

def main():
    """Main setup function"""
    
    print("🚀 Setting up ETL Invoice Processing Demo Data")
    print("=" * 50)
    
    # Create directory structure
    invoices_dir = create_demo_structure()
    
    # Check for existing files
    has_files = check_existing_files(invoices_dir)
    
    if not has_files:
        # Try to copy sample files
        copied = copy_sample_files(invoices_dir)
        
        if not copied:
            # Create placeholder files
            create_placeholder_files(invoices_dir)
    
    # Show next steps
    print("\n🎯 Next Steps:")
    print("1. Add your invoice PDF files to the data/invoices/ directory")
    print("2. Run the demo: python etl_invoice_demo.py")
    print("3. Check the demo output and database results")
    
    print("\n📚 For more information:")
    print("- See data/README.md for detailed usage instructions")
    print("- Check the main demo README for workflow details")
    
    # Show file size recommendations
    print("\n💡 File Size Recommendations:")
    print("- Individual files: 1-5 MB each")
    print("- Total demo data: 20-50 MB")
    print("- GitHub limit: 100 MB per file")
    print("- Repository limit: 1 GB total")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1) 