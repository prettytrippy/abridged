import fitz
from tkinter import filedialog
import io
from typing import Tuple

def validate_file(filename: str, file_bytes: bytes) -> Tuple[bool, str, str]:
    import os
    
    # Define supported file types
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt'}
    
    # Get file extension
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Validate file type
    if file_extension not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file type. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}", file_extension
    
    # Validate file isn't empty
    if len(file_bytes) == 0:
        return False, "Uploaded file is empty", file_extension
    
    return True, "", file_extension

def extract_text_from_pdf(pdf_bytes: bytes, start_page: int = 1, end_page: int = None) -> str:
    # Open PDF from bytes

    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    if start_page == -1 and end_page == -1:
        start_page = 0
        end_page = pdf_document.page_count

    else:
        start_page -= 1
        end_page -= 1

    if pdf_document.page_count < end_page:
        return f"Page number {end_page} is longer than the document to be summarized."

    extracted_text = ""
    for page_num in range(start_page, end_page):
        page = pdf_document.load_page(page_num)
        extracted_text += f"--- Page {page_num + 1} ---\n"
        extracted_text += page.get_text()
        extracted_text += "\n\n"
    
    pdf_document.close()
    
    return extracted_text

def extract_text_from_txt(txt_bytes: bytes) -> str:
    # Try common encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            return txt_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # Fallback with error handling
    return txt_bytes.decode('utf-8', errors='replace')

def process_file(file_bytes: bytes, file_extension: str, start_page: int, end_page: int) -> str:
    # Extract text based on file type
    if file_extension == '.pdf':
        extracted_text = extract_text_from_pdf(file_bytes, start_page, end_page)
    elif file_extension == '.txt':
        extracted_text = extract_text_from_txt(file_bytes)
    else:
        extracted_text = "Unknown file type."
    
    return extracted_text

def read_file(filename, file_bytes, start_page, end_page):
    quality, msg, file_extension = validate_file(filename, file_bytes)

    if not quality:
        return msg
    
    extracted_text = process_file(file_bytes, file_extension, start_page, end_page)
    return extracted_text

def read_file_uhh(pdf_path):
    text = ''
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    pdf_document.close()
    return text
    
def file_search():
    filepath = filedialog.askopenfilename() 
    return read_file_uhh(filepath)