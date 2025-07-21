from typing import Dict, Any, List


class TrustScoreCalculator:
    """Calculate overall trust scores"""

    def __init__(self):
        self.weights = {
            "resume": 0.3,
            "video": 0.4,
            "audio": 0.3
        }

    def calculate_mvp1_score(self, resume_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate trust score for MVP1 (resume only)"""
        ai_probability = resume_analysis["ai_probability"]

        # For MVP1, trust score is inverse of AI probability
        trust_score = 100 - ai_probability

        return {
            "overall_trust_score": round(trust_score, 1),
            "trust_level": self._get_trust_level(trust_score),
            "components": {
                "resume_authenticity": round(trust_score, 1),
                "video_authenticity": "Not analyzed (MVP2)",
                "audio_authenticity": "Not analyzed (MVP3)"
            },
            "recommendation": self._get_recommendation(trust_score),
            "next_steps": self._get_next_steps(trust_score)
        }

    def _get_trust_level(self, score: float) -> str:
        """Get trust level description"""
        if score >= 80:
            return "High Trust - Appears Authentic"
        elif score >= 60:
            return "Moderate Trust - Minor Concerns"
        elif score >= 40:
            return "Low Trust - Significant Concerns"
        else:
            return "Very Low Trust - Major Red Flags"

    def _get_recommendation(self, score: float) -> str:
        """Get hiring recommendation"""
        if score >= 80:
            return "✅ Proceed with standard evaluation process"
        elif score >= 60:
            return "⚠️ Proceed with additional verification steps"
        elif score >= 40:
            return "🔍 Requires thorough manual review before proceeding"
        else:
            return "🚫 High risk - recommend detailed investigation"

    def _get_next_steps(self, score: float) -> List[str]:
        """Suggest next steps based on score"""
        if score >= 80:
            return [
                "Continue with normal interview process",
                "Standard reference checks recommended"
            ]
        elif score >= 60:
            return [
                "Conduct detailed behavioral interview",
                "Verify specific accomplishments mentioned",
                "Request portfolio or work samples"
            ]
        elif score >= 40:
            return [
                "Extensive technical assessment required",
                "Multiple reference checks necessary",
                "Consider skills-based evaluation",
                "Request live demonstration of claimed abilities"
            ]
        else:
            return [
                "⚠️ Consider rejecting or flagging application",
                "If proceeding, require comprehensive verification",
                "Multiple rounds of assessment recommended",
                "Legal/compliance review may be necessary"
            ]
