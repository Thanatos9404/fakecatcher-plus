import traceback
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

try:
    from app.configure import settings
except ImportError:
    from configure import settings

# Enhanced analyzers
from ..core.ai_detection.ensemble import EnhancedResumeAnalyzer
from ..core.job_verification.job_analyzer import JobPostingAnalyzer
from ..utils.file_handler import FileHandler
from ..utils.validators import validate_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize analyzers
try:
    enhanced_analyzer = EnhancedResumeAnalyzer()
    job_analyzer = JobPostingAnalyzer()
    file_handler = FileHandler()
    logger.info("All analyzers initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize analyzers: {str(e)}")
    logger.error(traceback.format_exc())


# Existing resume analysis endpoint
@router.post("/analyze/resume")
async def analyze_resume_enhanced(file: UploadFile = File(...)):
    """Enhanced resume analysis with AI detection capabilities"""
    try:
        logger.info(f"Enhanced analysis request: {file.filename}, content_type: {file.content_type}")

        # Validate file
        validation_result = await validate_file(file, file_type="resume")
        if not validation_result["valid"]:
            logger.error(f"File validation failed: {validation_result['error']}")
            raise HTTPException(status_code=400, detail=validation_result["error"])

        logger.info("✅ File validation passed")

        # Extract text from file
        try:
            text_content = await file_handler.extract_text_from_resume(file)
            logger.info(f"✅ Text extraction successful, length: {len(text_content)} characters")
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")

        if not text_content.strip():
            logger.error("❌ No text content found in file")
            raise HTTPException(status_code=400, detail="No text content found in file")

        # Run comprehensive AI-enhanced analysis
        try:
            logger.info("🚀 Starting comprehensive AI-enhanced analysis...")
            comprehensive_result = await enhanced_analyzer.comprehensive_analysis(text_content)
            logger.info("✅ AI-enhanced analysis completed successfully")

            # Add metadata
            comprehensive_result.update({
                "file_info": {
                    "filename": file.filename,
                    "size_bytes": validation_result.get("file_size", 0),
                    "text_length": len(text_content),
                    "file_type": validation_result.get("file_extension", "unknown")
                },
                "processing_timestamp": "success"
            })

            return comprehensive_result

        except Exception as e:
            logger.error(f"❌ AI-enhanced analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in enhanced analyze_resume: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# NEW: Job posting analysis endpoints
@router.post("/analyze/job/upload")
async def analyze_job_upload(file: UploadFile = File(...)):
    """Analyze job posting from uploaded image or PDF"""
    try:
        logger.info(f"Job upload analysis request: {file.filename}, content_type: {file.content_type}")

        # Validate file type
        if file.content_type.startswith('image/'):
            input_type = 'image'
        elif file.content_type == 'application/pdf':
            input_type = 'pdf'
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload an image or PDF.")

        # Validate file size (max 10MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file position

        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

        logger.info(f"✅ File validation passed for {input_type}")

        # Run job posting analysis
        try:
            logger.info("🚀 Starting job posting analysis...")
            analysis_result = await job_analyzer.analyze_job_posting(input_type, file)
            logger.info("✅ Job posting analysis completed successfully")

            # Add file metadata
            analysis_result.update({
                "file_info": {
                    "filename": file.filename,
                    "size_bytes": file_size,
                    "file_type": input_type
                }
            })

            return analysis_result

        except Exception as e:
            logger.error(f"❌ Job posting analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Job analysis failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in job upload analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analyze/job/url")
async def analyze_job_url(job_url: str = Form(...)):
    """Analyze job posting from URL"""
    try:
        logger.info(f"Job URL analysis request: {job_url}")

        # Basic URL validation
        if not job_url.startswith(('http://', 'https://')):
            job_url = f"https://{job_url}"

        # Run job posting analysis
        try:
            logger.info("🚀 Starting job URL analysis...")
            analysis_result = await job_analyzer.analyze_job_posting('url', job_url)
            logger.info("✅ Job URL analysis completed successfully")

            # Add URL metadata
            analysis_result.update({
                "url_info": {
                    "source_url": job_url,
                    "analysis_type": "url_scraping"
                }
            })

            return analysis_result

        except Exception as e:
            logger.error(f"❌ Job URL analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Job URL analysis failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in job URL analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Health check endpoints
@router.get("/health/ai")
async def check_ai_health():
    """Check health status of AI detection components"""
    try:
        health_status = await enhanced_analyzer.health_check()
        return {
            "status": "success",
            "ai_health": health_status,
            "timestamp": "healthy"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "fallback_available": True
        }


@router.get("/health/job")
async def check_job_analyzer_health():
    """Check health status of job analyzer components"""
    try:
        health_status = await job_analyzer.health_check()
        return {
            "status": "success",
            "job_analyzer_health": health_status,
            "timestamp": "healthy"
        }
    except Exception as e:
        logger.error(f"Job analyzer health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "fallback_available": True
        }


# Keep existing route for backward compatibility
@router.post("/analyze/complete")
async def analyze_complete(
        resume_file: Optional[UploadFile] = File(None),
        video_file: Optional[UploadFile] = File(None),
        audio_file: Optional[UploadFile] = File(None)
):
    """Complete analysis for all file types (Future MVPs)"""
    return {
        "status": "coming_soon",
        "message": "Complete analysis will be available in MVP 2 & 3",
        "available_analysis": ["resume_ai_enhanced", "job_posting_verification"],
        "ai_detection": "now_available"
    }
