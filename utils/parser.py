import pdfplumber
import docx2txt
import os

def extract_text_pdf(file):
    """Extract text from a PDF file (path or UploadedFile)"""
    if hasattr(file, "read"):  # Streamlit UploadedFile
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    elif os.path.exists(file):  # file path
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    else:
        raise FileNotFoundError(f"{file} does not exist.")

def extract_text_docx(file):
    """Extract text from DOCX file (path or UploadedFile)"""
    if hasattr(file, "read"):  # UploadedFile
        with open("temp.docx", "wb") as f:
            f.write(file.getbuffer())
        text = docx2txt.process("temp.docx")
        os.remove("temp.docx")
        return text.strip()
    elif os.path.exists(file):
        text = docx2txt.process(file)
        return text.strip()
    else:
        raise FileNotFoundError(f"{file} does not exist.")

def extract_text(file):
    """Detect file type and extract text"""
    if hasattr(file, "name"):
        filename = file.name
    else:
        filename = file

    if filename.endswith(".pdf"):
        return extract_text_pdf(file)
    elif filename.endswith(".docx"):
        return extract_text_docx(file)
    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")
