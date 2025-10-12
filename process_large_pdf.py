#!/usr/bin/env python3
"""
Chunked PDF Processor for Large Documents
Processes PDFs in manageable page chunks to avoid read timeout errors
"""

import sys
import os
from pathlib import Path

def process_pdf_in_chunks(pdf_path: str, chunk_size: int = 20, output_dir: str = None):
    """
    Process a large PDF by splitting it into smaller chunks

    Args:
        pdf_path: Path to the PDF file
        chunk_size: Number of pages per chunk (default: 20)
        output_dir: Directory to save chunk files (default: same as PDF)
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("Installing PyMuPDF...")
        os.system("pip install pymupdf")
        import fitz

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        return

    # Setup output directory
    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}_chunks"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True)

    # Open PDF
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    print(f"📄 Processing: {pdf_path.name}")
    print(f"📊 Total pages: {total_pages}")
    print(f"📦 Chunk size: {chunk_size} pages")
    print(f"📁 Output directory: {output_dir}")
    print()

    chunks_created = []

    # Process in chunks
    for start_page in range(0, total_pages, chunk_size):
        end_page = min(start_page + chunk_size, total_pages)
        chunk_num = (start_page // chunk_size) + 1

        # Create new PDF for this chunk
        chunk_doc = fitz.open()
        chunk_doc.insert_pdf(doc, from_page=start_page, to_page=end_page-1)

        # Save chunk
        chunk_filename = f"{pdf_path.stem}_chunk_{chunk_num:03d}_pages_{start_page+1}-{end_page}.pdf"
        chunk_path = output_dir / chunk_filename
        chunk_doc.save(chunk_path)
        chunk_doc.close()

        chunk_size_mb = chunk_path.stat().st_size / (1024 * 1024)
        print(f"✅ Created: {chunk_filename} ({chunk_size_mb:.2f} MB)")

        chunks_created.append({
            'chunk_num': chunk_num,
            'filename': chunk_filename,
            'path': str(chunk_path),
            'start_page': start_page + 1,
            'end_page': end_page,
            'page_count': end_page - start_page
        })

    doc.close()

    # Create index file
    index_path = output_dir / "chunk_index.txt"
    with open(index_path, 'w') as f:
        f.write(f"Source PDF: {pdf_path}\n")
        f.write(f"Total pages: {total_pages}\n")
        f.write(f"Chunk size: {chunk_size} pages\n")
        f.write(f"Total chunks: {len(chunks_created)}\n\n")
        f.write("Chunk Index:\n")
        f.write("-" * 80 + "\n")
        for chunk in chunks_created:
            f.write(f"Chunk {chunk['chunk_num']:3d}: Pages {chunk['start_page']:3d}-{chunk['end_page']:3d} | {chunk['filename']}\n")

    print()
    print(f"📋 Index created: {index_path}")
    print(f"✨ Total chunks created: {len(chunks_created)}")
    print()
    print("Next steps:")
    print(f"  1. Process individual chunks with: Read tool on each chunk PDF")
    print(f"  2. Or extract text with: pdftotext <chunk_file>.pdf")
    print(f"  3. Chunk directory: {output_dir}")

    return chunks_created

def extract_chunk_text(chunk_pdf_path: str, output_txt_path: str = None):
    """Extract text from a chunk PDF to a text file"""
    try:
        import fitz
    except ImportError:
        os.system("pip install pymupdf")
        import fitz

    chunk_path = Path(chunk_pdf_path)
    if output_txt_path is None:
        output_txt_path = chunk_path.with_suffix('.txt')

    doc = fitz.open(chunk_path)
    text_content = []

    for page_num, page in enumerate(doc, 1):
        text_content.append(f"--- Page {page_num} ---\n")
        text_content.append(page.get_text())
        text_content.append("\n\n")

    doc.close()

    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(''.join(text_content))

    print(f"✅ Extracted text to: {output_txt_path}")
    return output_txt_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <pdf_path> [chunk_size] [output_dir]")
        print()
        print("Examples:")
        print(f"  {sys.argv[0]} document.pdf")
        print(f"  {sys.argv[0]} document.pdf 30")
        print(f"  {sys.argv[0]} document.pdf 20 ./chunks")
        sys.exit(1)

    pdf_path = sys.argv[1]
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None

    process_pdf_in_chunks(pdf_path, chunk_size, output_dir)
