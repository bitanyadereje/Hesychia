import pdfplumber
import os

def extract_and_save():
    pdf_path = "data/isaac_of_nineveh_mystical_treatises_text.pdf"
    output_path = "data/st_isaac_clean.txt"
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: PDF not found at {pdf_path}")
        return
    
    print("📄 Extracting text from PDF with pdfplumber...")
    full_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                full_text += text + "\n\n"
            else:
                print(f"⚠️ Page {page_num} had no extractable text (may be a scanned image).")
    
    if not full_text.strip():
        print("❌ FAILURE: No readable text found. The PDF is likely a scanned image (photos of pages).")
        print("   You will need to use an OCR tool or find a text-based PDF version.")
        return
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"✅ SUCCESS! Clean text saved to: {output_path}")
    print(f"   Extracted about {len(full_text)} characters.")
    print("   Now delete your Pinecone index and re-run ingest.py with this clean file.")

if __name__ == "__main__":
    extract_and_save()