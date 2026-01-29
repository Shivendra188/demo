import fitz  # PyMuPDF

def read_policy_pdf(file_path: str) -> str:
    text = "policy.pdf"
    doc = fitz.open(file_path)

    for page in doc:
        text += page.get_text()

    return text
