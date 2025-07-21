from fastapi import UploadFile
from typing import Dict, List
import os
from ..configure import settings


async def validate_file(file: UploadFile, file_type: str) -> Dict[str, any]:
    """Validate uploaded file based on type"""

    # Get file extension
    file_extension = os.path.splitext(file.filename.lower())[1]

    # Define allowed extensions based on file type
    allowed_extensions = {
        "resume": settings.ALLOWED_RESUME_EXTENSIONS,
        "video": settings.ALLOWED_VIDEO_EXTENSIONS,
        "audio": settings.ALLOWED_AUDIO_EXTENSIONS
    }

    # Check if file type is supported
    if file_type not in allowed_extensions:
        return {
            "valid": False,
            "error": f"Unsupported file type: {file_type}"
        }

    # Check file extension
    if file_extension not in allowed_extensions[file_type]:
        return {
            "valid": False,
            "error": f"File extension {file_extension} not allowed for {file_type}. Allowed: {', '.join(allowed_extensions[file_type])}"
        }

    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)

    # Reset file position for further reading
    await file.seek(0)

    if file_size > settings.MAX_FILE_SIZE:
        return {
            "valid": False,
            "error": f"File size ({file_size / (1024 * 1024):.1f}MB) exceeds maximum allowed size ({settings.MAX_FILE_SIZE / (1024 * 1024):.1f}MB)"
        }

    # Check if file is empty
    if file_size == 0:
        return {
            "valid": False,
            "error": "File is empty"
        }

    return {
        "valid": True,
        "file_size": file_size,
        "file_extension": file_extension
    }
