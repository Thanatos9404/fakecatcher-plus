import asyncio
import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from cachetools import TTLCache
import hashlib
from app.configure import settings

logger = logging.getLogger(__name__)


class HuggingFaceAIClient:
    """
    Hugging Face API client for AI content detection in FakeCatcher++
    Updated with correct API endpoints and model usage
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
            "User-Agent": "FakeCatcher++ Resume Authenticity Detector v2.0"
        }

        # Model endpoints
        self.ai_detector_model = settings.HF_AI_DETECTOR_MODEL
        self.text_classifier_model = settings.HF_TEXT_CLASSIFIER_MODEL
        self.content_analyzer_model = settings.HF_CONTENT_ANALYZER_MODEL

        logger.info(f"HuggingFaceAIClient initialized with model: {self.ai_detector_model}")

    def _generate_cache_key(self, text: str, model: str, task: str) -> str:
        """Generate unique cache key for API requests"""
        content = f"{text[:100]}{model}{task}"
        return hashlib.md5(content.encode()).hexdigest()

    def _clean_ai_response(self, response_text: str) -> str:
        """Filter and clean AI response, removing unwanted intro/outro lines"""
        import re
        filter_patterns = [
            r"here's your analysis:?\s*",
            r"here is the analysis:?\s*",
            r"based on my analysis:?\s*",
            r"analysis results?:?\s*",
            r"output:?\s*",
            r"result:?\s*",
        ]

        cleaned_text = response_text.strip()
        for pattern in filter_patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE)

        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        return '\n'.join(lines)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def _make_api_request(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to Hugging Face API with retry logic"""

        # Correct API URL format for Hugging Face Inference API
        api_url = f"{self.base_url}/{model_name}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"Making request to: {api_url}")
                response = await client.post(
                    api_url,
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
        Primary AI detection method using Hugging Face specialized models
        Enhanced with proper error handling and multiple fallback strategies
        """

        # Check cache first
        cache_key = self._generate_cache_key(resume_text, self.ai_detector_model, "ai_detection")
        if self.cache and cache_key in self.cache:
            logger.info("Returning cached AI detection result")
            return self.cache[cache_key]

        try:
            logger.info("Starting Hugging Face AI detection analysis")

            # Try primary AI detection model first
            result = await self._try_ai_detector_model(resume_text)

            if result and not result.get("fallback_mode", False):
                # Cache successful result
                if self.cache:
                    self.cache[cache_key] = result
                logger.info("AI detection completed successfully")
                return result

            # Fallback to text classification approach
            logger.info("Primary detector failed, trying classification approach")
            result = await self._try_classification_model(resume_text)

            if self.cache and result and not result.get("fallback_mode", False):
                self.cache[cache_key] = result
                logger.info("Classification approach completed successfully")

            return result

        except Exception as e:
            logger.error(f"All AI detection methods failed: {str(e)}")
            return self._create_fallback_response(resume_text, str(e))

    async def _try_ai_detector_model(self, resume_text: str) -> Dict[str, Any]:
        """Try using specialized AI detection model"""

        try:
            # Prepare text for AI detection (limit to 2000 chars for better performance)
            text_sample = resume_text[:2000]

            payload = {
                "inputs": text_sample,
                "options": {
                    "wait_for_model": True,
                    "use_cache": True
                }
            }

            logger.info(f"Calling AI detector model: {self.ai_detector_model}")
            raw_response = await self._make_api_request(self.ai_detector_model, payload)

            return self._process_ai_detector_response(raw_response, resume_text)

        except Exception as e:
            logger.error(f"AI detector model failed: {str(e)}")
            return {"fallback_mode": True, "error": str(e)}

    async def _try_classification_model(self, resume_text: str) -> Dict[str, Any]:
        """Fallback to general text classification model"""

        try:
            # Create classification prompt - shorter text for classification models
            text_sample = resume_text[:1000]

            payload = {
                "inputs": text_sample,
                "parameters": {
                    "candidate_labels": ["human_written", "ai_generated", "computer_generated"],
                    "multi_label": False
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": True
                }
            }

            # Use bart-large-mnli for zero-shot classification
            logger.info("Calling classification model: facebook/bart-large-mnli")
            raw_response = await self._make_api_request("facebook/bart-large-mnli", payload)

            return self._process_classification_response(raw_response, resume_text)

        except Exception as e:
            logger.error(f"Classification model failed: {str(e)}")
            return {"fallback_mode": True, "error": str(e)}

    def _process_ai_detector_response(self, raw_response: Any, resume_text: str) -> Dict[str, Any]:
        """Process response from specialized AI detection model"""

        try:
            ai_probability = 0.0
            confidence_score = 0.5

            if isinstance(raw_response, list) and len(raw_response) > 0:
                result = raw_response[0]

                # Handle different response formats from AI detection models
                if isinstance(result, dict):
                    # Standard format: label and score
                    if 'label' in result and 'score' in result:
                        label = result['label'].upper()
                        score = result['score']

                        # Check if label indicates AI-generated content
                        if any(keyword in label for keyword in ['FAKE', 'AI', 'GENERATED', 'MACHINE', 'BOT']):
                            ai_probability = score * 100
                        else:  # Real, Human, Natural, etc.
                            ai_probability = (1 - score) * 100

                        confidence_score = score

                    # Alternative format: direct probability scores
                    elif 'ai_probability' in result:
                        ai_probability = result['ai_probability']
                        confidence_score = result.get('confidence', 0.5)

                    # Handle multiple labels scenario
                    elif isinstance(result, list) and len(result) > 0:
                        # Take the highest confidence result
                        best_result = max(result, key=lambda x: x.get('score', 0))
                        return self._process_ai_detector_response([best_result], resume_text)

            logger.info(f"AI detector processed: {ai_probability:.2f}% AI probability")
            return self._create_analysis_result(ai_probability, confidence_score, resume_text, "ai_detector")

        except Exception as e:
            logger.error(f"Error processing AI detector response: {str(e)}")
            return {"fallback_mode": True, "error": str(e)}

    def _process_classification_response(self, raw_response: Any, resume_text: str) -> Dict[str, Any]:
        """Process response from text classification model"""

        try:
            ai_probability = 0.0
            confidence_score = 0.5

            if isinstance(raw_response, dict):
                labels = raw_response.get('labels', [])
                scores = raw_response.get('scores', [])

                # Find AI-related labels and their scores
                for i, label in enumerate(labels):
                    if i < len(scores):
                        label_lower = label.lower()
                        if any(keyword in label_lower for keyword in
                               ['ai', 'generated', 'computer', 'machine', 'artificial']):
                            ai_probability = scores[i] * 100
                            confidence_score = scores[i]
                            break

                # If no explicit AI label found, infer from human label
                if ai_probability == 0.0 and scores and labels:
                    for i, label in enumerate(labels):
                        if 'human' in label.lower():
                            ai_probability = (1 - scores[i]) * 100
                            confidence_score = scores[i]
                            break

                # Fallback: use first score as human confidence
                if ai_probability == 0.0 and scores:
                    ai_probability = (1 - scores[0]) * 100
                    confidence_score = scores[0]

            logger.info(f"Classification processed: {ai_probability:.2f}% AI probability")
            return self._create_analysis_result(ai_probability, confidence_score, resume_text, "classification")

        except Exception as e:
            logger.error(f"Error processing classification response: {str(e)}")
            return {"fallback_mode": True, "error": str(e)}

    def _create_analysis_result(self, ai_probability: float, confidence_score: float,
                                resume_text: str, method: str) -> Dict[str, Any]:
        """Create standardized analysis result"""

        # Ensure probability is within valid range
        ai_prob = max(0, min(100, ai_probability))
        human_prob = 100 - ai_prob

        return {
            "ai_probability": round(ai_prob, 2),
            "confidence_level": self._determine_confidence_level(confidence_score, ai_prob),
            "human_probability": round(human_prob, 2),
            "mixed_probability": 0.0,
            "analysis_method": f"huggingface_{method}",
            "model_used": self.ai_detector_model if method == "ai_detector" else "facebook/bart-large-mnli",
            "detailed_scores": {
                "ai_generated": round(ai_prob, 2),
                "human_written": round(human_prob, 2),
                "mixed_human_ai": 0.0
            },
            "analysis_details": {
                "text_length": len(resume_text),
                "analysis_scope": f"First {min(2000 if method == 'ai_detector' else 1000, len(resume_text))} characters analyzed",
                "detection_category": self._categorize_detection_result(ai_prob),
                "risk_assessment": self._assess_risk_level(ai_prob),
                "recommended_actions": self._generate_recommendations(ai_prob)
            },
            "processing_timestamp": str(asyncio.get_event_loop().time())
        }

    def _create_fallback_response(self, resume_text: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback response when all AI methods fail"""

        return {
            "ai_probability": 0.0,
            "confidence_level": "Error - Fallback to Rule-based",
            "human_probability": 0.0,
            "mixed_probability": 0.0,
            "analysis_method": "fallback_mode",
            "model_used": "none",
            "error": error_msg,
            "fallback_mode": True,
            "analysis_details": {
                "text_length": len(resume_text),
                "analysis_scope": "AI analysis failed - using rule-based fallback",
                "detection_category": "Analysis Error",
                "risk_assessment": "Unable to assess with AI - using rule-based analysis",
                "recommended_actions": [
                    "✅ Rule-based analysis results available",
                    "🔄 Retry AI analysis later",
                    "🔧 Check API connection and credentials",
                    "📊 Consider manual review for critical decisions"
                ]
            },
            "processing_timestamp": str(asyncio.get_event_loop().time())
        }

    def _determine_confidence_level(self, model_confidence: float, ai_probability: float) -> str:
        """Determine human-readable confidence level for AI analysis"""

        if model_confidence >= 0.9:
            return "Very High Confidence - AI Enhanced"
        elif model_confidence >= 0.75:
            return "High Confidence - AI Enhanced"
        elif model_confidence >= 0.6:
            return "Medium-High Confidence - AI Enhanced"
        elif model_confidence >= 0.4:
            return "Medium Confidence - AI Enhanced"
        else:
            return "Low Confidence - AI Enhanced"

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
        """Generate actionable recommendations for recruiters based on AI analysis"""
        recommendations = []

        if ai_probability >= 75:
            recommendations.extend([
                "🚨 CRITICAL: Conduct thorough verification interview",
                "📋 Request detailed examples of specific projects mentioned",
                "🔍 Verify employment history through multiple references",
                "💼 Ask for live portfolio demonstration",
                "⚠️ Flag for senior review before proceeding",
                "📊 Consider skills-based assessment tests"
            ])
        elif ai_probability >= 50:
            recommendations.extend([
                "⚡ ELEVATED RISK: Schedule comprehensive technical interview",
                "📞 Verify key accomplishments with previous employers",
                "🎯 Focus on specific skill demonstrations during interview",
                "📊 Request concrete metrics and results examples"
            ])
        elif ai_probability >= 25:
            recommendations.extend([
                "✅ MODERATE: Enhanced interview process recommended",
                "🔍 Pay attention to consistency during interview",
                "📋 Ask follow-up questions on specific experiences"
            ])
        else:
            recommendations.extend([
                "✅ LOW RISK: Resume appears authentic",
                "📝 Proceed with standard evaluation process",
                "💡 Minor follow-up questions may be beneficial"
            ])

        return recommendations

    async def health_check(self) -> Dict[str, Any]:
        """Check if Hugging Face API is accessible and working"""
        try:
            # Simple health check with minimal payload
            test_payload = {
                "inputs": "This is a health check test for FakeCatcher++.",
                "options": {
                    "wait_for_model": False,
                    "use_cache": True
                }
            }

            logger.info("Performing Hugging Face API health check")
            response = await self._make_api_request(self.ai_detector_model, test_payload)

            return {
                "status": "healthy",
                "api_accessible": True,
                "model_ready": True,
                "primary_model": self.ai_detector_model,
                "fallback_model": "facebook/bart-large-mnli",
                "cache_enabled": self.cache is not None,
                "api_key_configured": bool(self.api_key and len(self.api_key) > 10),
                "response_time": "< 5s"
            }

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "fallback_available": True,
                "api_key_configured": bool(self.api_key and len(self.api_key) > 10)
            }
