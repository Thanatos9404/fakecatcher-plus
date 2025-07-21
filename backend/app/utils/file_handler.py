from fastapi import UploadFile
import fitz  # PyMuPDF
import docx
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FileHandler:
    """Handle file operations and text extraction"""

    def __init__(self):
        logger.info("FileHandler initialized")

    async def extract_text_from_resume(self, file: UploadFile) -> str:
        """Extract text content from resume file"""

        if not file.filename:
            raise ValueError("No filename provided")

        file_extension = file.filename.lower().split('.')[-1]
        logger.info(f"Processing file with extension: {file_extension}")

        try:
            if file_extension == 'pdf':
                return await self._extract_from_pdf_pymupdf(file)
            elif file_extension in ['doc', 'docx']:
                return await self._extract_from_docx(file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

        except Exception as e:
            logger.error(f"Failed to extract text from {file_extension}: {str(e)}")
            raise Exception(f"Failed to extract text from {file_extension}: {str(e)}")

    async def _extract_from_pdf_pymupdf(self, file: UploadFile) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            # Read file content
            content = await file.read()
            logger.info(f"Read PDF content, size: {len(content)} bytes")

            if len(content) == 0:
                raise ValueError("PDF file is empty")

            # Open PDF from memory
            pdf_doc = fitz.open(stream=content, filetype="pdf")
            logger.info(f"PDF opened successfully, pages: {pdf_doc.page_count}")

            text = ""
            for page_num in range(pdf_doc.page_count):
                try:
                    page = pdf_doc[page_num]
                    page_text = page.get_text()
                    if page_text:
                        text += page_text + "\n"
                        logger.info(f"Extracted text from page {page_num + 1}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")

            pdf_doc.close()

            # Reset file position
            await file.seek(0)

            logger.info(f"Total extracted text length: {len(text)}")
            return text.strip()

        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {str(e)}")
            # Fallback to basic extraction
            await file.seek(0)
            content = await file.read()

            # Try to extract as plain text
            try:
                text = content.decode('utf-8', errors='ignore')
                await file.seek(0)
                return text
            except:
                raise Exception(f"Could not extract text from PDF: {str(e)}")

    async def _extract_from_docx(self, file: UploadFile) -> str:
        """Extract text from DOCX file"""
        try:
            content = await file.read()
            logger.info(f"Read DOCX content, size: {len(content)} bytes")

            if len(content) == 0:
                raise ValueError("DOCX file is empty")

            doc = docx.Document(io.BytesIO(content))

            text = ""
            paragraph_count = 0
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
                    paragraph_count += 1

            logger.info(f"Extracted text from {paragraph_count} paragraphs")

            # Reset file position
            await file.seek(0)

            return text.strip()

        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            raise Exception(f"Could not extract text from DOCX: {str(e)}")
