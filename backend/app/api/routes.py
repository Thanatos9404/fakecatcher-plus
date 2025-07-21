import traceback
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from ..core.resume.analyzer import ResumeAnalyzer
from ..core.trust_score import TrustScoreCalculator
from ..utils.file_handler import FileHandler
from ..utils.validators import validate_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize analyzers
try:
    resume_analyzer = ResumeAnalyzer()
    trust_calculator = TrustScoreCalculator()
    file_handler = FileHandler()
    logger.info("All analyzers initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize analyzers: {str(e)}")
    logger.error(traceback.format_exc())


@router.post("/analyze/resume")
async def analyze_resume(file: UploadFile = File(...)):
    """Analyze uploaded resume for AI-generated content"""
    try:
        logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")

        # Validate file
        validation_result = await validate_file(file, file_type="resume")
        if not validation_result["valid"]:
            logger.error(f"File validation failed: {validation_result['error']}")
            raise HTTPException(status_code=400, detail=validation_result["error"])

        logger.info("File validation passed")

        # Extract text from file
        try:
            text_content = await file_handler.extract_text_from_resume(file)
            logger.info(f"Text extraction successful, length: {len(text_content)}")
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")

        if not text_content.strip():
            logger.error("No text content found in file")
            raise HTTPException(status_code=400, detail="No text content found in file")

        # Analyze for AI content
        try:
            logger.info("Starting AI analysis...")
            analysis_result = await resume_analyzer.analyze_text(text_content)
            logger.info("AI analysis completed successfully")
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

        # Calculate trust score
        try:
            trust_score = trust_calculator.calculate_mvp1_score(analysis_result)
            logger.info("Trust score calculated successfully")
        except Exception as e:
            logger.error(f"Trust score calculation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Trust score calculation failed: {str(e)}")

        return {
            "status": "success",
            "analysis": analysis_result,
            "trust_score": trust_score,
            "mvp_version": "1"
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_resume: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
