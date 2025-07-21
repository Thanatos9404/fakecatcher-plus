import asyncio
import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from cachetools import TTLCache
import hashlib
from config import settings

logger = logging.getLogger(__name__)


class HuggingFaceAIClient:
    """
    Hugging Face API client for AI content detection in FakeCatcher++
    Specialized for resume authenticity verification with advanced prompt engineering
    """

    def __init__(self):
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.base_url = settings.HF_API_URL
        self.timeout = settings.TIMEOUT_SECONDS

        # Initialize cache for API responses
        self.cache = TTLCache(maxsize=1000, ttl=settings.AI_CACHE_DURATION) if settings.AI_CACHE_ENABLED else None

        # HTTP client with proper headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "FakeCatcher++ Resume Authenticity Detector v1.0"
        }

    def _generate_cache_key(self, text: str, model: str, task: str) -> str:
        """Generate unique cache key for API requests"""
        content = f"{text[:100]}{model}{task}"  # Use first 100 chars + model + task
        return hashlib.md5(content.encode()).hexdigest()

    def _clean_ai_response(self, response_text: str) -> str:
        """
        Filter and clean AI response, removing unwanted intro/outro lines
        that commonly appear in AI model outputs
        """
        # Common AI response patterns to remove
        filter_patterns = [
            r"here's your analysis:?\s*",
            r"here is the analysis:?\s*",
            r"based on my analysis:?\s*",
            r"analysis results?:?\s*",
            r"output:?\s*",
            r"result:?\s*",
            r"response:?\s*",
            r"i hope this helps:?\s*",
            r"let me know if you need:?\s*",
            r"please note:?\s*",
            r"disclaimer:?\s*",
            r"^(sure|certainly|of course)[,.]?\s*",
            r"^(i can help|i'll analyze|let me analyze)\s+.*$",
        ]

        import re
        cleaned_text = response_text.strip()

        # Remove common AI intro/outro patterns
        for pattern in filter_patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE)

        # Remove extra whitespace and empty lines
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        return '\n'.join(lines)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def _make_api_request(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to Hugging Face API with retry logic"""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/{model_name}",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except httpx.TimeoutException:
                logger.error(f"Request timeout for model {model_name}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error calling HF API: {str(e)}")
                raise

    async def detect_ai_generated_content(self, resume_text: str) -> Dict[str, Any]:
        """
        Primary AI detection method using specialized resume authenticity analysis
        with advanced prompt engineering for maximum accuracy
        """

        # Check cache first
        cache_key = self._generate_cache_key(resume_text, settings.HF_AI_DETECTOR_MODEL, "ai_detection")
        if self.cache and cache_key in self.cache:
            logger.info("Returning cached AI detection result")
            return self.cache[cache_key]

        # Craft highly detailed prompt for AI detection
        prompt = self._create_ai_detection_prompt(resume_text)

        try:
            # Use text classification model for AI detection
            payload = {
                "inputs": prompt,
                "parameters": {
                    "candidate_labels": ["human_written", "ai_generated", "mixed_human_ai"],
                    "multi_label": False,
                    "return_all_scores": True
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }

            raw_response = await self._make_api_request(
                "facebook/bart-large-mnli",  # Better for classification
                payload
            )

            # Process and clean the response
            processed_result = self._process_ai_detection_response(raw_response, resume_text)

            # Cache the result
            if self.cache:
                self.cache[cache_key] = processed_result

            return processed_result

        except Exception as e:
            logger.error(f"AI detection failed: {str(e)}")
            return {
                "ai_probability": 0.0,
                "confidence_level": "Error - Fallback to Rule-based",
                "error": str(e),
                "fallback_mode": True
            }

    def _create_ai_detection_prompt(self, resume_text: str) -> str:
        """
        Create a comprehensive, professionally engineered prompt for AI detection
        Designed specifically for FakeCatcher++ resume authenticity verification
        """

        prompt = f"""
RESUME AUTHENTICITY ANALYSIS TASK

Project Context: FakeCatcher++ - Advanced AI-powered resume authenticity verification system
Objective: Detect AI-generated content in professional resumes with high accuracy for recruitment integrity

Analysis Requirements:
1. Determine if the resume content is human-written, AI-generated, or mixed (human-edited AI content)
2. Focus on professional resume-specific patterns and characteristics
3. Consider modern AI writing capabilities (GPT-4, Claude, Gemini, etc.)
4. Evaluate authenticity indicators specific to career documents

Key Detection Criteria:
- Writing style naturalness and human imperfections
- Professional experience authenticity patterns
- Skill description genuineness vs. generic AI templates
- Career progression logic and timeline consistency
- Industry-specific terminology usage accuracy
- Personal voice and individual character presence
- Subtle AI writing fingerprints in professional context

Resume Content to Analyze:
{resume_text[:2000]}...

Classification Categories:
- human_written: Genuine human-authored content with natural imperfections and authentic personal voice
- ai_generated: Content showing clear AI generation patterns, template-like structure, or artificial perfection
- mixed_human_ai: Human-edited AI content or AI-assisted writing with human modifications

Provide precise classification focusing on resume authenticity for recruitment verification purposes.
"""
        return prompt.strip()

    def _process_ai_detection_response(self, raw_response: Dict, resume_text: str) -> Dict[str, Any]:
        """Process and structure the AI detection response for FakeCatcher++"""

        try:
            # Extract classification results
            if isinstance(raw_response, list) and len(raw_response) > 0:
                scores = raw_response[0]
                labels = scores.get('labels', [])
                confidences = scores.get('scores', [])
            else:
                # Handle different response formats
                labels = raw_response.get('labels', [])
                confidences = raw_response.get('scores', [])

            # Calculate AI probability from classification scores
            ai_probability = 0.0
            human_probability = 0.0
            mixed_probability = 0.0

            for label, confidence in zip(labels, confidences):
                if 'ai_generated' in label.lower():
                    ai_probability = confidence * 100
                elif 'human_written' in label.lower():
                    human_probability = confidence * 100
                elif 'mixed' in label.lower():
                    mixed_probability = confidence * 100

            # Calculate final AI probability (mixed counts as partial AI)
            final_ai_prob = ai_probability + (mixed_probability * 0.6)

            # Determine confidence level
            max_confidence = max(confidences) if confidences else 0
            confidence_level = self._determine_confidence_level(max_confidence, final_ai_prob)

            # Generate detailed analysis
            analysis_details = self._generate_analysis_details(final_ai_prob, resume_text)

            return {
                "ai_probability": round(final_ai_prob, 2),
                "confidence_level": confidence_level,
                "human_probability": round(human_probability, 2),
                "mixed_probability": round(mixed_probability, 2),
                "analysis_method": "huggingface_text_classification",
                "model_used": "facebook/bart-large-mnli",
                "detailed_scores": {
                    "ai_generated": round(ai_probability, 2),
                    "human_written": round(human_probability, 2),
                    "mixed_human_ai": round(mixed_probability, 2)
                },
                "analysis_details": analysis_details,
                "processing_timestamp": str(asyncio.get_event_loop().time())
            }

        except Exception as e:
            logger.error(f"Error processing AI detection response: {str(e)}")
            return {
                "ai_probability": 0.0,
                "confidence_level": "Error in processing",
                "error": str(e),
                "fallback_mode": True
            }

    def _determine_confidence_level(self, model_confidence: float, ai_probability: float) -> str:
        """Determine human-readable confidence level for the AI detection"""

        if model_confidence >= 0.9 and (ai_probability >= 80 or ai_probability <= 20):
            return "Very High Confidence"
        elif model_confidence >= 0.8 and (ai_probability >= 70 or ai_probability <= 30):
            return "High Confidence"
        elif model_confidence >= 0.6:
            return "Medium Confidence"
        elif model_confidence >= 0.4:
            return "Low Confidence"
        else:
            return "Very Low Confidence - Manual Review Recommended"

    def _generate_analysis_details(self, ai_probability: float, resume_text: str) -> Dict[str, Any]:
        """Generate detailed analysis insights for the detection result"""

        word_count = len(resume_text.split())

        details = {
            "text_length": word_count,
            "analysis_scope": "Full resume content" if word_count <= 2000 else "First 2000 characters analyzed",
            "detection_category": self._categorize_detection_result(ai_probability),
            "risk_assessment": self._assess_risk_level(ai_probability),
            "recommended_actions": self._generate_recommendations(ai_probability)
        }

        return details

    def _categorize_detection_result(self, ai_probability: float) -> str:
        """Categorize the detection result for recruiters"""
        if ai_probability >= 85:
            return "Highly Likely AI-Generated"
        elif ai_probability >= 65:
            return "Probably AI-Generated"
        elif ai_probability >= 35:
            return "Mixed/Uncertain - Requires Review"
        elif ai_probability >= 15:
            return "Probably Human-Written"
        else:
            return "Likely Human-Written"

    def _assess_risk_level(self, ai_probability: float) -> str:
        """Assess hiring risk level based on AI probability"""
        if ai_probability >= 80:
            return "HIGH RISK - Strong AI indicators detected"
        elif ai_probability >= 60:
            return "MEDIUM-HIGH RISK - Multiple AI patterns found"
        elif ai_probability >= 40:
            return "MEDIUM RISK - Some AI characteristics present"
        elif ai_probability >= 20:
            return "LOW-MEDIUM RISK - Minor concerns identified"
        else:
            return "LOW RISK - Appears authentic"

    def _generate_recommendations(self, ai_probability: float) -> List[str]:
        """Generate actionable recommendations for recruiters"""
        recommendations = []

        if ai_probability >= 75:
            recommendations.extend([
                "🚨 Conduct thorough verification interview",
                "📋 Request detailed examples of specific projects mentioned",
                "🔍 Verify employment history through references",
                "💼 Ask for portfolio or work samples demonstration",
                "⚠️ Consider this a high-priority screening case"
            ])
        elif ai_probability >= 50:
            recommendations.extend([
                "✅ Schedule comprehensive technical interview",
                "📞 Verify key accomplishments with previous employers",
                "🎯 Focus on specific skill demonstrations during interview",
                "📊 Request concrete metrics and results examples"
            ])
        elif ai_probability >= 25:
            recommendations.extend([
                "✅ Standard interview process recommended",
                "🔍 Pay attention to consistency during interview",
                "📋 Ask follow-up questions on specific experiences"
            ])
        else:
            recommendations.append("✅ Resume appears authentic - proceed with standard evaluation")

        return recommendations

    async def health_check(self) -> Dict[str, Any]:
        """Check if Hugging Face API is accessible and working"""
        try:
            # Simple test with a small classification task
            test_payload = {
                "inputs": "This is a test message for FakeCatcher++ health check.",
                "parameters": {"candidate_labels": ["test", "health_check"]},
                "options": {"wait_for_model": False}
            }

            response = await self._make_api_request("facebook/bart-large-mnli", test_payload)

            return {
                "status": "healthy",
                "api_accessible": True,
                "model_ready": True,
                "cache_enabled": self.cache is not None,
                "response_time": "< 5s"
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "fallback_available": True
            }
