#!/usr/bin/env python3
"""
PDF Content Analysis
This script analyzes PDF files to understand their structure and content
"""

import os
import sys
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image
import io
sys.path.append('/Users/tarpus/memra')

def analyze_pdf_with_pypdf2(pdf_path: str):
    """Analyze PDF using PyPDF2"""
    print(f"📄 Analyzing PDF with PyPDF2: {pdf_path}")
    print("=" * 60)
    
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        
        print(f"✅ PDF loaded successfully")
        print(f"📊 Pages: {len(reader.pages)}")
        print(f"📋 Metadata: {reader.metadata}")
        
        total_text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            total_text += f"\n--- PAGE {i+1} ---\n{page_text}\n"
            print(f"📄 Page {i+1} text length: {len(page_text)} characters")
            if len(page_text) > 0:
                print(f"📄 Page {i+1} preview: {page_text[:200]}...")
        
        print(f"📝 Total text length: {len(total_text)} characters")
        
        return {
            "success": True,
            "pages": len(reader.pages),
            "total_text_length": len(total_text),
            "text_content": total_text
        }
        
    except Exception as e:
        print(f"❌ PyPDF2 analysis failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def analyze_pdf_with_pymupdf(pdf_path: str):
    """Analyze PDF using PyMuPDF (more advanced)"""
    print(f"\n🔍 Analyzing PDF with PyMuPDF: {pdf_path}")
    print("=" * 60)
    
    try:
        doc = fitz.open(pdf_path)
        
        print(f"✅ PDF loaded successfully")
        print(f"📊 Pages: {len(doc)}")
        print(f"📋 Metadata: {doc.metadata}")
        
        total_text = ""
        for i, page in enumerate(doc):
            page_text = page.get_text()
            total_text += f"\n--- PAGE {i+1} ---\n{page_text}\n"
            print(f"📄 Page {i+1} text length: {len(page_text)} characters")
            if len(page_text) > 0:
                print(f"📄 Page {i+1} preview: {page_text[:200]}...")
            
            # Check for images
            image_list = page.get_images()
            if image_list:
                print(f"🖼️  Page {i+1} contains {len(image_list)} images")
        
        print(f"📝 Total text length: {len(total_text)} characters")
        
        doc.close()
        
        return {
            "success": True,
            "pages": len(doc),
            "total_text_length": len(total_text),
            "text_content": total_text
        }
        
    except Exception as e:
        print(f"❌ PyMuPDF analysis failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def check_pdf_images(pdf_path: str):
    """Check if PDF contains images that might need OCR"""
    print(f"\n🖼️  Checking PDF for images: {pdf_path}")
    print("=" * 60)
    
    try:
        doc = fitz.open(pdf_path)
        
        total_images = 0
        for i, page in enumerate(doc):
            image_list = page.get_images()
            if image_list:
                print(f"📄 Page {i+1}: {len(image_list)} images found")
                total_images += len(image_list)
                
                for j, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    print(f"   Image {j+1}: {pix.width}x{pix.height} pixels, {pix.n} colors")
                    pix = None
        
        if total_images == 0:
            print("📄 No images found in PDF")
        else:
            print(f"🖼️  Total images found: {total_images}")
        
        doc.close()
        
        return {
            "success": True,
            "total_images": total_images
        }
        
    except Exception as e:
        print(f"❌ Image analysis failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main analysis function"""
    print("🔍 PDF CONTENT ANALYSIS")
    print("=" * 80)
    
    # Test with a specific invoice file
    pdf_path = os.path.abspath("data/invoices/10352259401.PDF")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"📁 Analyzing: {pdf_path}")
    print(f"📁 File size: {os.path.getsize(pdf_path)} bytes")
    
    # Step 1: Analyze with PyPDF2
    pypdf2_result = analyze_pdf_with_pypdf2(pdf_path)
    
    # Step 2: Analyze with PyMuPDF
    pymupdf_result = analyze_pdf_with_pymupdf(pdf_path)
    
    # Step 3: Check for images
    image_result = check_pdf_images(pdf_path)
    
    # Summary
    print(f"\n📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"PyPDF2 Text Length: {pypdf2_result.get('total_text_length', 0)} characters")
    print(f"PyMuPDF Text Length: {pymupdf_result.get('total_text_length', 0)} characters")
    print(f"Images Found: {image_result.get('total_images', 0)}")
    
    if pymupdf_result.get('total_text_length', 0) > pypdf2_result.get('total_text_length', 0):
        print(f"✅ PyMuPDF extracted more text than PyPDF2")
    elif pymupdf_result.get('total_text_length', 0) == 0:
        print(f"❌ Both extractors found no text - PDF may be image-based")
        print(f"💡 This explains why the system falls back to mock data!")
    else:
        print(f"⚠️  Both extractors found minimal text")

if __name__ == "__main__":
    main() 