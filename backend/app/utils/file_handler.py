from fastapi import UploadFile
import fitz  # PyMuPDF
import docx
import io
from typing import Optional


class FileHandler:
    """Handle file operations and text extraction"""

    def __init__(self):
        pass

    async def extract_text_from_resume(self, file: UploadFile) -> str:
        """Extract text content from resume file"""

        file_extension = file.filename.lower().split('.')[-1]

        try:
            if file_extension == 'pdf':
                return await self._extract_from_pdf_pymupdf(file)
            elif file_extension in ['doc', 'docx']:
                return await self._extract_from_docx(file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

        except Exception as e:
            raise Exception(f"Failed to extract text from {file_extension}: {str(e)}")

    async def _extract_from_pdf_pymupdf(self, file: UploadFile) -> str:
        """Extract text from PDF using PyMuPDF"""
        content = await file.read()

        # Open PDF from memory
        pdf_doc = fitz.open(stream=content, filetype="pdf")

        text = ""
        for page_num in range(pdf_doc.page_count):
            page = pdf_doc[page_num]
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"

        pdf_doc.close()

        # Reset file position
        await file.seek(0)

        return text.strip()

    async def _extract_from_docx(self, file: UploadFile) -> str:
        """Extract text from DOCX file"""
        content = await file.read()
        doc = docx.Document(io.BytesIO(content))

        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"

        # Reset file position
        await file.seek(0)

        return text.strip()
