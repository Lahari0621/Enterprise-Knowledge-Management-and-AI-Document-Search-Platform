from pathlib import Path
def extract(path,name):
    ext=Path(name).suffix.lower()
    if ext=='.txt': return Path(path).read_text(encoding='utf-8',errors='ignore')
    if ext=='.pdf':
        try:
            from PyPDF2 import PdfReader
            return '\n'.join(p.extract_text() or '' for p in PdfReader(path).pages)
        except Exception:return ''
    if ext=='.docx':
        try:
            from docx import Document
            return '\n'.join(p.text for p in Document(path).paragraphs)
        except Exception:return ''
    return ''

extract_text = extract
