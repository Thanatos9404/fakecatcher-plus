import logging
from typing import Dict, Any, List, Optional
from ..resume.analyzer import ResumeAnalyzer
from .hf_client import HuggingFaceAIClient
from ..trust_score import TrustScoreCalculator
from app.configure import settings

logger = logging.getLogger(__name__)


class EnhancedResumeAnalyzer:
    """
    Advanced ensemble system combining rule-based analysis with Hugging Face AI detection
    Designed for maximum accuracy in resume authenticity verification
    """

    def __init__(self):
        self.rule_analyzer = ResumeAnalyzer()
        self.ai_client = HuggingFaceAIClient()
        self.trust_calculator = TrustScoreCalculator()

        # Ensemble configuration from settings
        self.ai_weight = settings.AI_ENSEMBLE_WEIGHT
        self.rule_weight = settings.RULE_BASED_WEIGHT
        self.ai_enabled = settings.AI_DETECTION_ENABLED

        logger.info(f"EnhancedResumeAnalyzer initialized - AI enabled: {self.ai_enabled}, AI weight: {self.ai_weight}")

    async def comprehensive_analysis(self, resume_text: str) -> Dict[str, Any]:
        """
        Run comprehensive analysis combining multiple detection methods
        Returns enhanced results with AI-powered insights
        """

        logger.info(f"Starting comprehensive analysis (AI enabled: {self.ai_enabled})")

        try:
            # Always run rule-based analysis first (provides baseline + fallback)
            rule_results = await self.rule_analyzer.analyze_text(resume_text)
            logger.info("Rule-based analysis completed successfully")

            # Initialize analysis result structure
            analysis_result = {
                "analysis_method": "rule_based_only",
                "ai_enhanced": False,
                "rule_based_analysis": rule_results,
                "ai_analysis": None,
                "ensemble_score": rule_results["ai_probability"],
                "confidence_boost": 0.0,
                "processing_details": {
                    "rule_based_completed": True,
                    "ai_analysis_attempted": False,
                    "ai_analysis_successful": False,
                    "fallback_reason": None
                }
            }

            # Attempt AI analysis if enabled and API key available
            if self.ai_enabled and self.ai_client.api_key:
                try:
                    logger.info("Starting Hugging Face AI analysis")
                    analysis_result["processing_details"]["ai_analysis_attempted"] = True

                    ai_results = await self.ai_client.detect_ai_generated_content(resume_text)

                    # Check if AI analysis was successful
                    if not ai_results.get("fallback_mode", False):
                        # Successful AI analysis - create ensemble
                        logger.info("AI analysis successful - creating ensemble")
                        ensemble_analysis = self._create_ensemble_analysis(rule_results, ai_results, resume_text)

                        analysis_result.update({
                            "analysis_method": "ai_enhanced_ensemble",
                            "ai_enhanced": True,
                            "ai_analysis": ai_results,
                            "ensemble_score": ensemble_analysis["final_ai_probability"],
                            "confidence_boost": ensemble_analysis["confidence_improvement"],
                            "enhanced_insights": ensemble_analysis["enhanced_insights"],
                            "processing_details": {
                                "rule_based_completed": True,
                                "ai_analysis_attempted": True,
                                "ai_analysis_successful": True,
                                "ensemble_method": "weighted_average",
                                "ai_weight": self.ai_weight,
                                "rule_weight": self.rule_weight,
                                "ai_model_used": ai_results.get("model_used", "unknown")
                            }
                        })

                        logger.info(
                            f"AI-enhanced ensemble analysis completed - Final score: {ensemble_analysis['final_ai_probability']}%")
                    else:
                        # AI analysis failed but returned fallback data
                        analysis_result["ai_analysis"] = ai_results
                        analysis_result["processing_details"]["ai_analysis_attempted"] = True
                        analysis_result["processing_details"]["fallback_reason"] = ai_results.get("error",
                                                                                                  "AI service unavailable")
                        logger.warning("AI analysis failed, using rule-based results only")

                except Exception as e:
                    logger.error(f"AI analysis error: {str(e)}")
                    analysis_result["ai_error"] = str(e)
                    analysis_result["processing_details"]["ai_analysis_attempted"] = True
                    analysis_result["processing_details"]["fallback_reason"] = f"Exception: {str(e)}"
            else:
                if not self.ai_enabled:
                    analysis_result["processing_details"]["fallback_reason"] = "AI detection disabled in configuration"
                    logger.info("AI analysis disabled in configuration")
                elif not self.ai_client.api_key:
                    analysis_result["processing_details"]["fallback_reason"] = "Hugging Face API key not configured"
                    logger.info("AI analysis skipped - API key not configured")

            # Calculate enhanced trust score
            trust_score = await self._calculate_enhanced_trust_score(analysis_result)

            # Build comprehensive result
            comprehensive_result = {
                "status": "success",
                "analysis": {
                    "ai_probability": analysis_result["ensemble_score"],
                    "confidence_level": self._determine_overall_confidence(analysis_result),
                    "analysis_method": analysis_result["analysis_method"],
                    "ai_enhanced": analysis_result["ai_enhanced"],
                    "text_statistics": rule_results.get("text_statistics", {}),
                    "ai_patterns": rule_results.get("ai_patterns", {}),
                    "keyword_analysis": rule_results.get("keyword_analysis", {}),
                    "suspicious_sections": rule_results.get("suspicious_sections", []),
                    "recommendations": self._generate_enhanced_recommendations(analysis_result),
                    "processing_details": analysis_result["processing_details"]
                },
                "trust_score": trust_score,
                "mvp_version": "2_ai_enhanced",
                "detailed_analysis": analysis_result  # Full technical details for debugging
            }

            logger.info(f"Comprehensive analysis completed - Method: {analysis_result['analysis_method']}")
            return comprehensive_result

        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {str(e)}")
            raise Exception(f"Analysis pipeline error: {str(e)}")

    def _create_ensemble_analysis(self, rule_results: Dict, ai_results: Dict, resume_text: str) -> Dict[str, Any]:
        """Create weighted ensemble analysis combining rule-based and AI results"""

        rule_probability = rule_results.get("ai_probability", 0)
        ai_probability = ai_results.get("ai_probability", 0)

        # Weighted ensemble calculation
        ensemble_probability = (ai_probability * self.ai_weight) + (rule_probability * self.rule_weight)

        # Calculate confidence improvement
        rule_confidence = self._extract_confidence_score(rule_results.get("confidence_level", ""))
        ai_confidence = self._extract_confidence_score(ai_results.get("confidence_level", ""))
        confidence_improvement = max(0, ai_confidence - rule_confidence)

        # Determine method agreement
        score_difference = abs(ai_probability - rule_probability)
        consensus_strength = "Strong" if score_difference <= 15 else "Moderate" if score_difference <= 30 else "Weak"

        # Enhanced insights from AI analysis
        enhanced_insights = {
            "ai_model_assessment": ai_results.get("analysis_details", {}),
            "ensemble_agreement": round(score_difference, 2),
            "method_consensus": consensus_strength,
            "ai_specific_findings": ai_results.get("detailed_scores", {}),
            "risk_assessment": ai_results.get("analysis_details", {}).get("risk_assessment", "Unknown"),
            "detection_category": ai_results.get("analysis_details", {}).get("detection_category", "Unknown"),
            "model_used": ai_results.get("model_used", "unknown"),
            "analysis_scope": ai_results.get("analysis_details", {}).get("analysis_scope", "unknown")
        }

        logger.info(
            f"Ensemble created: Rule={rule_probability}%, AI={ai_probability}%, Final={ensemble_probability:.2f}%")

        return {
            "final_ai_probability": round(ensemble_probability, 2),
            "confidence_improvement": round(confidence_improvement, 2),
            "enhanced_insights": enhanced_insights,
            "component_scores": {
                "rule_based": rule_probability,
                "ai_based": ai_probability,
                "ensemble": ensemble_probability
            },
            "consensus_analysis": {
                "agreement_level": consensus_strength,
                "score_difference": round(score_difference, 2),
                "reliability_indicator": "High" if score_difference <= 10 else "Medium" if score_difference <= 25 else "Low"
            }
        }

    def _extract_confidence_score(self, confidence_text: str) -> float:
        """Extract numerical confidence from confidence level text"""
        confidence_map = {
            "very high": 95,
            "high": 85,
            "medium-high": 75,
            "medium": 65,
            "low-medium": 50,
            "low": 40,
            "very low": 20
        }

        confidence_text = confidence_text.lower()
        for key, value in confidence_map.items():
            if key in confidence_text:
                return value
        return 50  # Default medium confidence

    def _determine_overall_confidence(self, analysis_result: Dict) -> str:
        """Determine overall confidence level for the comprehensive analysis"""

        if analysis_result["ai_enhanced"]:
            confidence_boost = analysis_result.get("confidence_boost", 0)
            ensemble_score = analysis_result["ensemble_score"]

            # Consider both confidence boost and score certainty
            if confidence_boost >= 20 and (ensemble_score >= 80 or ensemble_score <= 20):
                return "Very High Confidence - AI Enhanced"
            elif confidence_boost >= 15 and (ensemble_score >= 70 or ensemble_score <= 30):
                return "High Confidence - AI Enhanced"
            elif confidence_boost >= 10:
                return "Medium-High Confidence - AI Enhanced"
            else:
                return "Medium Confidence - AI Enhanced"
        else:
            # Rule-based confidence levels
            ai_prob = analysis_result["ensemble_score"]
            if ai_prob >= 80 or ai_prob <= 20:
                return "High Confidence - Rule-based"
            elif ai_prob >= 70 or ai_prob <= 30:
                return "Medium Confidence - Rule-based"
            else:
                return "Low Confidence - Rule-based (Recommend AI retry)"

    def _generate_enhanced_recommendations(self, analysis_result: Dict) -> List[str]:
        """Generate enhanced recommendations based on comprehensive analysis"""

        base_recommendations = []
        ai_probability = analysis_result["ensemble_score"]
        is_ai_enhanced = analysis_result["ai_enhanced"]

        # Base recommendations based on AI probability
        if ai_probability >= 85:
            base_recommendations.extend([
                "🚨 CRITICAL ALERT: Very high likelihood of AI-generated content",
                "🔍 Mandatory comprehensive verification process required",
                "📋 Request detailed work samples and live portfolio demonstration",
                "📞 Conduct multiple reference checks with previous employers",
                "⚠️ Escalate to senior review team before any hiring decision",
                "🎯 Consider skills-based practical assessments"
            ])
        elif ai_probability >= 70:
            base_recommendations.extend([
                "⚠️ HIGH RISK: Strong AI generation indicators present",
                "🎯 Conduct thorough technical and behavioral interviews",
                "📊 Verify specific metrics and accomplishments mentioned",
                "💼 Request live demonstration of claimed technical skills",
                "📋 Ask for detailed explanations of project methodologies"
            ])
        elif ai_probability >= 50:
            base_recommendations.extend([
                "⚡ MODERATE RISK: Notable AI patterns detected",
                "✅ Enhanced interview process with detailed questioning",
                "🔍 Focus on experience-specific and scenario-based questions",
                "📋 Verify key claims through targeted follow-up questions"
            ])
        elif ai_probability >= 25:
            base_recommendations.extend([
                "💡 LOW-MODERATE RISK: Minor AI indicators present",
                "📝 Standard plus interview with additional verification",
                "✅ Ask for specific examples of mentioned experiences"
            ])
        else:
            base_recommendations.extend([
                "✅ LOW RISK: Resume appears largely authentic",
                "📝 Standard evaluation process appropriate",
                "💡 Routine verification questions sufficient"
            ])

        # Add AI-specific insights if available
        if is_ai_enhanced and "enhanced_insights" in analysis_result:
            insights = analysis_result["enhanced_insights"]
            consensus = insights.get("method_consensus", "Unknown")

            if consensus == "Strong":
                base_recommendations.append("🤝 Multiple detection methods agree - high reliability score")
            elif consensus == "Moderate":
                base_recommendations.append("🔄 Mixed signals detected - recommend additional manual review")
            else:
                base_recommendations.append("⚠️ Conflicting analysis results - manual expert review recommended")

            # Add AI model-specific recommendations
            ai_analysis = analysis_result.get("ai_analysis", {})
            if "analysis_details" in ai_analysis and "recommended_actions" in ai_analysis["analysis_details"]:
                ai_recommendations = ai_analysis["analysis_details"]["recommended_actions"]
                # Add top AI-specific recommendations (limit to avoid overwhelming)
                base_recommendations.extend(ai_recommendations[:2])

        # Add fallback information if AI analysis failed
        processing_details = analysis_result.get("processing_details", {})
        if not processing_details.get("ai_analysis_successful", False) and processing_details.get(
                "ai_analysis_attempted", False):
            fallback_reason = processing_details.get("fallback_reason", "Unknown error")
            base_recommendations.append(
                f"ℹ️ Note: AI analysis unavailable ({fallback_reason}) - using rule-based analysis")

        return base_recommendations

    async def _calculate_enhanced_trust_score(self, analysis_result: Dict) -> Dict[str, Any]:
        """Calculate enhanced trust score incorporating AI analysis results"""

        # Create analysis object compatible with trust score calculator
        mock_analysis = {
            "ai_probability": analysis_result["ensemble_score"],
            "confidence_level": self._determine_overall_confidence(analysis_result)
        }

        # Get base trust score
        base_trust_score = self.trust_calculator.calculate_mvp1_score(mock_analysis)

        # Enhance trust score if AI analysis was successful
        if analysis_result["ai_enhanced"]:
            confidence_boost = analysis_result.get("confidence_boost", 0)

            # Apply AI confidence boost to trust score (capped improvement)
            enhanced_score = base_trust_score["overall_trust_score"]
            if confidence_boost >= 15:
                enhanced_score += min(5, confidence_boost / 4)  # Max 5 point improvement
            elif confidence_boost >= 10:
                enhanced_score += min(3, confidence_boost / 5)  # Max 3 point improvement

            # Update trust score with AI enhancements
            base_trust_score.update({
                "overall_trust_score": round(enhanced_score, 1),
                "trust_level": self._get_enhanced_trust_level(enhanced_score),
                "ai_enhancement_applied": True,
                "confidence_boost": confidence_boost,
                "components": {
                    "resume_authenticity": round(enhanced_score, 1),
                    "ai_verification": f"AI Enhanced ({analysis_result.get('ai_analysis', {}).get('model_used', 'HuggingFace')})",
                    "video_authenticity": "Not analyzed (MVP2)",
                    "audio_authenticity": "Not analyzed (MVP3)"
                }
            })
        else:
            # Add information about why AI enhancement wasn't applied
            processing_details = analysis_result.get("processing_details", {})
            fallback_reason = processing_details.get("fallback_reason", "Unknown")

            base_trust_score["components"]["ai_verification"] = f"Rule-based only ({fallback_reason})"

        return base_trust_score

    def _get_enhanced_trust_level(self, score: float) -> str:
        """Get enhanced trust level description"""
        if score >= 90:
            return "Exceptional Trust - AI Verified Authentic"
        elif score >= 80:
            return "Very High Trust - AI Enhanced Verification"
        elif score >= 70:
            return "High Trust - AI Assisted Analysis"
        elif score >= 60:
            return "Moderate Trust - AI Enhanced Assessment"
        elif score >= 40:
            return "Low Trust - AI Detected Concerns"
        else:
            return "Very Low Trust - AI Flagged High Risk"

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all analysis components"""

        health_status = {
            "overall_status": "healthy",
            "rule_analyzer": "operational",
            "ai_detection": "unknown",
            "ensemble_ready": False,
            "configuration": {
                "ai_enabled": self.ai_enabled,
                "ai_weight": self.ai_weight,
                "rule_weight": self.rule_weight
            }
        }

        # Check AI client health if enabled
        if self.ai_enabled:
            try:
                ai_health = await self.ai_client.health_check()
                health_status["ai_detection"] = ai_health["status"]
                health_status["ensemble_ready"] = ai_health["api_accessible"]
                health_status["ai_details"] = ai_health
            except Exception as e:
                health_status["ai_detection"] = f"error: {str(e)}"
                health_status["ensemble_ready"] = False
                health_status["ai_error"] = str(e)
        else:
            health_status["ai_detection"] = "disabled"
            health_status["ensemble_ready"] = False

        # Determine overall system status
        if health_status["ai_detection"] == "healthy" and health_status["ensemble_ready"]:
            health_status["overall_status"] = "fully_operational_ai_enhanced"
        elif health_status["rule_analyzer"] == "operational":
            health_status["overall_status"] = "operational_rule_based_fallback"
        else:
            health_status["overall_status"] = "degraded"

        logger.info(f"Health check completed: {health_status['overall_status']}")
        return health_status
