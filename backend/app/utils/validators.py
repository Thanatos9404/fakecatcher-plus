import logging
from typing import Dict, Any, List
from fastapi import UploadFile
from app.configure import settings

logger = logging.getLogger(__name__)


async def validate_file(file: UploadFile, file_type: str = "resume") -> Dict[str, Any]:
    """Enhanced file validation for resumes and job postings"""

    validation_result = {
        "valid": False,
        "error": None,
        "file_size": 0,
        "file_extension": None,
        "content_type": file.content_type
    }

    try:
        # Get file size
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file position

        validation_result["file_size"] = file_size

        # Check file size limits
        max_size = settings.MAX_FILE_SIZE
        if file_size > max_size:
            validation_result[
                "error"] = f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
            return validation_result

        if file_size == 0:
            validation_result["error"] = "File is empty"
            return validation_result

        # Get file extension
        filename = file.filename or ""
        if "." not in filename:
            validation_result["error"] = "File must have a valid extension"
            return validation_result

        file_extension = "." + filename.split(".")[-1].lower()
        validation_result["file_extension"] = file_extension

        # Validate file types based on context
        allowed_extensions = {
            "resume": settings.ALLOWED_RESUME_EXTENSIONS,
            "job_posting": settings.ALLOWED_RESUME_EXTENSIONS + [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            # Add image formats for job postings
            "video": settings.ALLOWED_VIDEO_EXTENSIONS,
            "audio": settings.ALLOWED_AUDIO_EXTENSIONS
        }

        valid_extensions = allowed_extensions.get(file_type, settings.ALLOWED_RESUME_EXTENSIONS)

        if file_extension not in valid_extensions:
            validation_result[
                "error"] = f"File type {file_extension} not allowed for {file_type}. Allowed types: {', '.join(valid_extensions)}"
            return validation_result

        # Validate content type
        valid_content_types = {
            ".pdf": ["application/pdf"],
            ".doc": ["application/msword"],
            ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
            ".jpg": ["image/jpeg"],
            ".jpeg": ["image/jpeg"],
            ".png": ["image/png"],
            ".gif": ["image/gif"],
            ".bmp": ["image/bmp"]
        }

        expected_content_types = valid_content_types.get(file_extension, [])
        if expected_content_types and file.content_type not in expected_content_types:
            logger.warning(f"Content type mismatch: expected {expected_content_types}, got {file.content_type}")
            # Don't fail validation for content type mismatch, just log it

        validation_result["valid"] = True
        logger.info(f"File validation successful: {filename} ({file_size} bytes)")

    except Exception as e:
        logger.error(f"File validation error: {str(e)}")
        validation_result["error"] = f"File validation failed: {str(e)}"

    return validation_result


async def validate_url(url: str) -> Dict[str, Any]:
    """Validate job posting URL"""

    validation_result = {
        "valid": False,
        "error": None,
        "url": url,
        "domain": None,
        "is_secure": False
    }

    try:
        from urllib.parse import urlparse

        if not url or not url.strip():
            validation_result["error"] = "URL cannot be empty"
            return validation_result

        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            validation_result["url"] = url

        # Parse URL
        parsed = urlparse(url)

        if not parsed.netloc:
            validation_result["error"] = "Invalid URL format"
            return validation_result

        validation_result["domain"] = parsed.netloc
        validation_result["is_secure"] = parsed.scheme == 'https'

        # Check for suspicious URL patterns
        suspicious_patterns = ['bit.ly', 'tinyurl', 'goo.gl', 't.co']
        if any(pattern in parsed.netloc for pattern in suspicious_patterns):
            validation_result["error"] = "Shortened URLs are not allowed for security reasons"
            return validation_result

        # Check URL length
        if len(url) > 2048:
            validation_result["error"] = "URL is too long"
            return validation_result

        validation_result["valid"] = True
        logger.info(f"URL validation successful: {url}")

    except Exception as e:
        logger.error(f"URL validation error: {str(e)}")
        validation_result["error"] = f"URL validation failed: {str(e)}"

    return validation_result
