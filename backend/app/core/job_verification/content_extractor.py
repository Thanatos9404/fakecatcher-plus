import asyncio
import logging
import re
from typing import Dict, Any, Optional, List
from fastapi import UploadFile
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)


class JobContentExtractor:
    """Extract job posting content from various sources"""

    def __init__(self):
        # Configure OCR settings
        self.ocr_config = r'--oem 3 --psm 6 -l eng'
        logger.info("JobContentExtractor initialized")

    async def extract_from_image(self, image_file: UploadFile) -> Dict[str, Any]:
        """Extract text from uploaded image using OCR"""
        try:
            # Read image content
            image_content = await image_file.read()
            image = Image.open(io.BytesIO(image_content))

            # Perform OCR
            extracted_text = pytesseract.image_to_string(image, config=self.ocr_config)

            # Reset file position
            await image_file.seek(0)

            job_content = self._parse_job_content(extracted_text)
            job_content['extraction_method'] = 'ocr_image'
            job_content['raw_text'] = extracted_text

            logger.info(f"OCR extraction completed, text length: {len(extracted_text)}")
            return job_content

        except Exception as e:
            logger.error(f"Image text extraction failed: {str(e)}")
            raise Exception(f"Failed to extract text from image: {str(e)}")

    async def extract_from_pdf(self, pdf_file: UploadFile) -> Dict[str, Any]:
        """Extract text from PDF job posting"""
        try:
            content = await pdf_file.read()
            pdf_doc = fitz.open(stream=content, filetype="pdf")

            extracted_text = ""
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                page_text = page.get_text()
                if page_text:
                    extracted_text += page_text + "\n"

            pdf_doc.close()
            await pdf_file.seek(0)

            job_content = self._parse_job_content(extracted_text)
            job_content['extraction_method'] = 'pdf_text'
            job_content['raw_text'] = extracted_text

            logger.info(f"PDF extraction completed, text length: {len(extracted_text)}")
            return job_content

        except Exception as e:
            logger.error(f"PDF text extraction failed: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    async def extract_from_url(self, job_url: str) -> Dict[str, Any]:
        """Extract job posting content from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                async with session.get(job_url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to access URL: HTTP {response.status}")

                    html_content = await response.text()

            # Parse HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            extracted_text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in extracted_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            extracted_text = '\n'.join(chunk for chunk in chunks if chunk)

            job_content = self._parse_job_content(extracted_text)
            job_content['extraction_method'] = 'web_scraping'
            job_content['raw_text'] = extracted_text
            job_content['source_url'] = job_url
            job_content['domain'] = urlparse(job_url).netloc

            logger.info(f"URL extraction completed for {job_url}, text length: {len(extracted_text)}")
            return job_content

        except Exception as e:
            logger.error(f"URL extraction failed for {job_url}: {str(e)}")
            raise Exception(f"Failed to extract content from URL: {str(e)}")

    def _parse_job_content(self, raw_text: str) -> Dict[str, Any]:
        """Parse extracted text to identify job posting components"""

        job_content = {
            'job_title': self._extract_job_title(raw_text),
            'company_name': self._extract_company_name(raw_text),
            'salary_range': self._extract_salary_info(raw_text),
            'location': self._extract_location(raw_text),
            'job_description': self._extract_job_description(raw_text),
            'requirements': self._extract_requirements(raw_text),
            'contact_info': self._extract_contact_info(raw_text),
            'application_method': self._extract_application_method(raw_text),
            'posting_date': self._extract_posting_date(raw_text),
            'red_flag_keywords': self._detect_red_flag_keywords(raw_text)
        }

        return job_content

    def _extract_job_title(self, text: str) -> Optional[str]:
        """Extract job title from text"""
        # Common patterns for job titles
        title_patterns = [
            r'(?:job title|position|role):\s*([^\n]+)',
            r'(\b(?:software|senior|junior|lead|principal|data|marketing|sales|customer|project|product|business|operations|human resources|hr|finance|accounting|graphic|web|mobile|backend|frontend|fullstack|devops|qa|quality assurance|analyst|manager|director|coordinator|specialist|engineer|developer|designer|architect|consultant|intern|entry level)\s+[^\n]{1,100})',
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fallback: first line that looks like a title
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 5 and len(line) < 100 and not line.lower().startswith(('http', 'www', 'email')):
                return line

        return None

    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name from text"""
        company_patterns = [
            r'(?:company|employer|organization):\s*([^\n]+)',
            r'(?:at|@)\s+([A-Z][a-zA-Z\s&.,]+(?:Inc|LLC|Corp|Ltd|Company|Co|Group|Solutions|Technologies|Systems|Services)?)',
            r'([A-Z][a-zA-Z\s&.,]+(?:Inc|LLC|Corp|Ltd|Company|Co|Group|Solutions|Technologies|Systems|Services))'
        ]

        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Filter out common false positives
                if len(company) > 2 and not any(
                        word in company.lower() for word in ['job', 'position', 'role', 'apply', 'click', 'here']):
                    return company

        return None

    def _extract_salary_info(self, text: str) -> Dict[str, Any]:
        """Extract salary information"""
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*[-to]+\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s+)?(hour|day|week|month|year|annually)?',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s+)?(hour|day|week|month|year|annually)',
            r'(\d{1,3}(?:,\d{3})*)\s*[-to]+\s*(\d{1,3}(?:,\d{3})*)\s*(?:per\s+)?(hour|day|week|month|year|annually)',
            r'competitive\s+salary|negotiable\s+salary|excellent\s+compensation'
        ]

        salary_info = {
            'found': False,
            'min_salary': None,
            'max_salary': None,
            'period': None,
            'raw_text': None,
            'is_suspicious': False
        }

        for pattern in salary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                match = matches[0]
                if isinstance(match, tuple) and len(match) >= 2:
                    salary_info['found'] = True
                    salary_info['raw_text'] = match
                    # Check for suspiciously high salaries (common scam indicator)
                    try:
                        if len(match) >= 2 and match[0].replace(',', '').isdigit():
                            min_sal = int(match[0].replace(',', ''))
                            if min_sal > 200000:  # Suspiciously high for most entry-level positions
                                salary_info['is_suspicious'] = True
                    except:
                        pass
                    break

        return salary_info

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract job location"""
        location_patterns = [
            r'(?:location|based in|located in):\s*([^\n]+)',
            r'([A-Z][a-zA-Z\s]+,\s+[A-Z]{2}(?:\s+\d{5})?)',  # City, State format
            r'(?:remote|work from home|telecommute|virtual)',
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1 if match.lastindex else 0).strip()

        return None

    def _extract_job_description(self, text: str) -> str:
        """Extract main job description"""
        # Look for description section
        desc_patterns = [
            r'(?:job description|description|responsibilities|duties):\s*(.*?)(?:\n\n|\nrequirements|\napply)',
            r'(?:about the role|role description):\s*(.*?)(?:\n\n|\nrequirements|\napply)'
        ]

        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        # Fallback: return first substantial paragraph
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if len(para) > 100:
                return para.strip()

        return text[:500] + "..." if len(text) > 500 else text

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract job requirements"""
        req_section = re.search(r'(?:requirements|qualifications|skills):\s*(.*?)(?:\n\n|\napply|\ncontact)', text,
                                re.IGNORECASE | re.DOTALL)

        if req_section:
            req_text = req_section.group(1)
            # Split by bullet points or line breaks
            requirements = [req.strip() for req in re.split(r'[•\-\*\n]', req_text) if
                            req.strip() and len(req.strip()) > 10]
            return requirements[:10]  # Limit to first 10 requirements

        return []

    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information"""
        contact_info = {
            'email': None,
            'phone': None,
            'website': None
        }

        # Email pattern
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact_info['email'] = email_match.group()

        # Phone pattern
        phone_match = re.search(r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
        if phone_match:
            contact_info['phone'] = phone_match.group()

        # Website pattern
        website_match = re.search(r'https?://[^\s]+', text)
        if website_match:
            contact_info['website'] = website_match.group()

        return contact_info

    def _extract_application_method(self, text: str) -> str:
        """Extract how to apply information"""
        apply_patterns = [
            r'(?:how to apply|apply|application):\s*([^\n]+)',
            r'(?:send|email|contact|apply).*?(?:resume|cv|application)',
        ]

        for pattern in apply_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1 if match.lastindex else 0).strip()

        return "Not specified"

    def _extract_posting_date(self, text: str) -> Optional[str]:
        """Extract posting date if available"""
        date_patterns = [
            r'(?:posted|date):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:posted|date):\s*([A-Za-z]+ \d{1,2}, \d{4})'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _detect_red_flag_keywords(self, text: str) -> List[str]:
        """Detect red flag keywords common in fake job postings"""
        red_flags = [
            'easy money', 'make money fast', 'work from home', 'no experience needed',
            'guaranteed income', 'unlimited earning potential', 'be your own boss',
            'financial freedom', 'pyramid', 'mlm', 'multi-level marketing',
            'pay upfront fee', 'training fee', 'starter kit', 'investment required',
            'wire transfer', 'western union', 'money gram', 'cash advance',
            'urgent hiring', 'immediate start', 'no interview required',
            'too good to be true', 'act now', 'limited time offer'
        ]

        found_flags = []
        text_lower = text.lower()

        for flag in red_flags:
            if flag in text_lower:
                found_flags.append(flag)

        return found_flags
