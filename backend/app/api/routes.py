from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import asyncio

from ..core.resume.analyzer import ResumeAnalyzer
from ..core.trust_score import TrustScoreCalculator
from ..utils.file_handler import FileHandler
from ..utils.validators import validate_file

router = APIRouter()

# Initialize analyzers
resume_analyzer = ResumeAnalyzer()
trust_calculator = TrustScoreCalculator()
file_handler = FileHandler()


@router.post("/analyze/resume")
async def analyze_resume(file: UploadFile = File(...)):
    """Analyze uploaded resume for AI-generated content"""
    try:
        # Validate file
        validation_result = await validate_file(file, file_type="resume")
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])

        # Extract text from file
        text_content = await file_handler.extract_text_from_resume(file)
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in file")

        # Analyze for AI content
        analysis_result = await resume_analyzer.analyze_text(text_content)

        # Calculate trust score (MVP1 - only resume)
        trust_score = trust_calculator.calculate_mvp1_score(analysis_result)

        return {
            "status": "success",
            "analysis": analysis_result,
            "trust_score": trust_score,
            "mvp_version": "1"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/complete")
async def analyze_complete(
        resume_file: Optional[UploadFile] = File(None),
        video_file: Optional[UploadFile] = File(None),
        audio_file: Optional[UploadFile] = File(None)
):
    """Complete analysis for all file types (Future MVPs)"""
    # This endpoint is prepared for future MVP phases
    return {
        "status": "coming_soon",
        "message": "Complete analysis will be available in MVP 2 & 3",
        "available_analysis": ["resume"]
    }
