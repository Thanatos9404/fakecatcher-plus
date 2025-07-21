import logging
from typing import Dict, Any, Optional
from ..resume.analyzer import ResumeAnalyzer
from .hf_client import HuggingFaceAIClient
from ..trust_score import TrustScoreCalculator
from config import settings

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

        # Ensemble configuration
        self.ai_weight = settings.AI_ENSEMBLE_WEIGHT  # 0.7
        self.rule_weight = settings.RULE_BASED_WEIGHT  # 0.3
        self.ai_enabled = settings.AI_DETECTION_ENABLED

    async def comprehensive_analysis(self, resume_text: str) -> Dict[str, Any]:
        """
        Run comprehensive analysis combining multiple detection methods
        Returns enhanced results with AI-powered insights
        """

        logger.info(f"Starting comprehensive analysis (AI enabled: {self.ai_enabled})")

        try:
            # Always run rule-based analysis (fallback + ensemble component)
            rule_results = await self.rule_analyzer.analyze_text(resume_text)
            logger.info("Rule-based analysis completed")

            # Initialize default structure
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
                    "ai_analysis_successful": False
                }
            }

            # Attempt AI analysis if enabled
            if self.ai_enabled and self.ai_client.api_key:
                try:
                    logger.info("Starting Hugging Face AI analysis")
                    ai_results = await self.ai_client.detect_ai_generated_content(resume_text)

                    if not ai_results.get("fallback_mode", False):
                        # Successful AI analysis - create ensemble
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
                                "rule_weight": self.rule_weight
                            }
                        })

                        logger.info("AI-enhanced ensemble analysis completed successfully")
                    else:
                        # AI analysis failed, but we have rule-based results
                        analysis_result["ai_analysis"] = ai_results
                        analysis_result["processing_details"]["ai_analysis_attempted"] = True
                        logger.warning("AI analysis failed, using rule-based results only")

                except Exception as e:
                    logger.error(f"AI analysis error: {str(e)}")
                    analysis_result["ai_error"] = str(e)
                    analysis_result["processing_details"]["ai_analysis_attempted"] = True
            else:
                logger.info("AI analysis disabled or API key missing")

            # Calculate enhanced trust score
            trust_score = await self._calculate_enhanced_trust_score(analysis_result)

            # Final comprehensive result
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
                "detailed_analysis": analysis_result  # Full technical details
            }

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

        # Enhanced insights from AI analysis
        enhanced_insights = {
            "ai_model_assessment": ai_results.get("analysis_details", {}),
            "ensemble_agreement": abs(ai_probability - rule_probability),
            "method_consensus": "Strong" if abs(ai_probability - rule_probability) <= 15 else "Weak",
            "ai_specific_findings": ai_results.get("detailed_scores", {}),
            "risk_assessment": ai_results.get("analysis_details", {}).get("risk_assessment", "Unknown")
        }

        return {
            "final_ai_probability": round(ensemble_probability, 2),
            "confidence_improvement": round(confidence_improvement, 2),
            "enhanced_insights": enhanced_insights,
            "component_scores": {
                "rule_based": rule_probability,
                "ai_based": ai_probability,
                "ensemble": ensemble_probability
            }
        }

    def _extract_confidence_score(self, confidence_text: str) -> float:
        """Extract numerical confidence from confidence level text"""
        confidence_map = {
            "very high": 95,
            "high": 85,
            "medium": 65,
            "low": 40,
            "very low": 20
        }

        confidence_text = confidence_text.lower()
        for key, value in confidence_map.items():
            if key in confidence_text:
                return value
        return 50  # Default medium confidence

    def _determine_overall_confidence(self, analysis_result: Dict) -> str:
        """Determine overall confidence level for the analysis"""

        if analysis_result["ai_enhanced"]:
            confidence_boost = analysis_result.get("confidence_boost", 0)
            if confidence_boost >= 20:
                return "Very High Confidence - AI Enhanced"
            elif confidence_boost >= 10:
                return "High Confidence - AI Enhanced"
            else:
                return "Medium-High Confidence - AI Enhanced"
        else:
            # Rule-based confidence levels
            ai_prob = analysis_result["ensemble_score"]
            if ai_prob >= 80 or ai_prob <= 20:
                return "High Confidence - Rule-based"
            elif ai_prob >= 70 or ai_prob <= 30:
                return "Medium Confidence - Rule-based"
            else:
                return "Low Confidence - Rule-based"

    def _generate_enhanced_recommendations(self, analysis_result: Dict) -> list:
        """Generate enhanced recommendations based on comprehensive analysis"""

        base_recommendations = []
        ai_probability = analysis_result["ensemble_score"]
        is_ai_enhanced = analysis_result["ai_enhanced"]

        # Base recommendations based on probability
        if ai_probability >= 85:
            base_recommendations.extend([
                "🚨 CRITICAL: Very high likelihood of AI-generated content detected",
                "🔍 Mandatory verification interview required",
                "📋 Request detailed work samples and portfolio demonstration",
                "📞 Comprehensive reference checks essential",
                "⚠️ Consider flagging for senior review before proceeding"
            ])
        elif ai_probability >= 70:
            base_recommendations.extend([
                "⚠️ HIGH RISK: Strong AI indicators present",
                "🎯 Conduct thorough technical assessment",
                "📊 Verify specific metrics and accomplishments",
                "💼 Request live demonstration of claimed skills"
            ])
        elif ai_probability >= 50:
            base_recommendations.extend([
                "⚡ MODERATE RISK: Some AI patterns detected",
                "✅ Enhanced interview process recommended",
                "🔍 Focus on experience-specific questioning",
                "📋 Verify key claims during interview"
            ])
        else:
            base_recommendations.extend([
                "✅ LOW RISK: Resume appears largely authentic",
                "📝 Standard evaluation process appropriate",
                "💡 Minor follow-up questions may be beneficial"
            ])

        # Add AI-specific insights if available
        if is_ai_enhanced and "enhanced_insights" in analysis_result:
            insights = analysis_result["enhanced_insights"]
            consensus = insights.get("method_consensus", "Unknown")

            if consensus == "Strong":
                base_recommendations.append("🤝 Multiple detection methods agree - high reliability")
            else:
                base_recommendations.append("🔄 Mixed signals detected - manual review recommended")

            # Add AI model specific recommendations
            ai_analysis = analysis_result.get("ai_analysis", {})
            if "recommended_actions" in ai_analysis:
                ai_recommendations = ai_analysis["recommended_actions"]
                base_recommendations.extend(ai_recommendations[:3])  # Add top 3 AI recommendations

        return base_recommendations

    async def _calculate_enhanced_trust_score(self, analysis_result: Dict) -> Dict[str, Any]:
        """Calculate enhanced trust score incorporating AI analysis results"""

        # Create a mock analysis object for trust score calculation
        mock_analysis = {
            "ai_probability": analysis_result["ensemble_score"],
            "confidence_level": self._determine_overall_confidence(analysis_result)
        }

        base_trust_score = self.trust_calculator.calculate_mvp1_score(mock_analysis)

        # Enhance trust score with AI insights
        if analysis_result["ai_enhanced"]:
            confidence_boost = analysis_result.get("confidence_boost", 0)

            # Adjust trust score based on AI confidence boost
            enhanced_score = base_trust_score["overall_trust_score"]
            if confidence_boost >= 15:
                enhanced_score += min(5, confidence_boost / 4)  # Cap improvement at 5 points

            base_trust_score.update({
                "overall_trust_score": round(enhanced_score, 1),
                "trust_level": self._get_enhanced_trust_level(enhanced_score),
                "ai_enhancement_applied": True,
                "confidence_boost": confidence_boost,
                "components": {
                    "resume_authenticity": round(enhanced_score, 1),
                    "ai_verification": "Enhanced with ML detection" if analysis_result[
                        "ai_enhanced"] else "Rule-based only",
                    "video_authenticity": "Not analyzed (MVP2)",
                    "audio_authenticity": "Not analyzed (MVP3)"
                }
            })

        return base_trust_score

    def _get_enhanced_trust_level(self, score: float) -> str:
        """Get enhanced trust level description"""
        if score >= 85:
            return "Very High Trust - AI Verified Authentic"
        elif score >= 75:
            return "High Trust - AI Enhanced Verification"
        elif score >= 60:
            return "Moderate Trust - AI Assisted Analysis"
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
            "ensemble_ready": False
        }

        # Check AI client health if enabled
        if self.ai_enabled:
            try:
                ai_health = await self.ai_client.health_check()
                health_status["ai_detection"] = ai_health["status"]
                health_status["ensemble_ready"] = ai_health["api_accessible"]
            except Exception as e:
                health_status["ai_detection"] = f"error: {str(e)}"
                health_status["ensemble_ready"] = False
        else:
            health_status["ai_detection"] = "disabled"
            health_status["ensemble_ready"] = False

        # Determine overall status
        if health_status["ai_detection"] == "healthy" and health_status["ensemble_ready"]:
            health_status["overall_status"] = "fully_operational_ai_enhanced"
        elif health_status["rule_analyzer"] == "operational":
            health_status["overall_status"] = "operational_rule_based_fallback"
        else:
            health_status["overall_status"] = "degraded"

        return health_status
