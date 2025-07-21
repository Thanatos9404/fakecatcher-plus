import traceback
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Optional

# Update imports to use new enhanced analyzer
from ..core.ai_detection.ensemble import EnhancedResumeAnalyzer
from ..core.trust_score import TrustScoreCalculator
from ..utils.file_handler import FileHandler
from ..utils.validators import validate_file
from app.configure import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize enhanced analyzers
try:
    enhanced_analyzer = EnhancedResumeAnalyzer()
    file_handler = FileHandler()
    logger.info("Enhanced AI analyzers initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize enhanced analyzers: {str(e)}")
    logger.error(traceback.format_exc())


@router.post("/analyze/resume")
async def analyze_resume_enhanced(file: UploadFile = File(...)):
    """
    Enhanced resume analysis with AI detection capabilities
    Combines rule-based analysis with Hugging Face AI models for maximum accuracy
    """
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
                "processing_timestamp": str(traceback.format_exc())[:100] if False else "success"
            })

            return comprehensive_result

        except Exception as e:
            logger.error(f"❌ AI-enhanced analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in enhanced analyze_resume: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health/ai")
async def check_ai_health():
    """Check health status of AI detection components"""
    try:
        health_status = await enhanced_analyzer.health_check()
        return {
            "status": "success",
            "ai_health": health_status,
            "timestamp": str(traceback.format_exc())[:100] if False else "healthy"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
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
        "available_analysis": ["resume_ai_enhanced"],
        "ai_detection": "now_available"
    }
