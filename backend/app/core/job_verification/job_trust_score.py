import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class JobTrustScoreCalculator:
    """Calculate comprehensive trust scores for job postings"""

    # Scoring weights for different components
    WEIGHT_DISTRIBUTION = {
        'content_authenticity': 0.30,  # AI analysis of job posting content
        'company_legitimacy': 0.25,  # Company verification results
        'web_intelligence': 0.20,  # Web presence and credibility
        'posting_source': 0.15,  # Source credibility (job board, company site)
        'red_flag_analysis': 0.10  # Scam pattern detection
    }

    def __init__(self):
        logger.info("JobTrustScoreCalculator initialized")

    def calculate_job_trust_score(self, analysis_components: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive trust score for job posting"""

        try:
            # Extract component scores
            content_score = self._calculate_content_score(analysis_components.get('content_analysis', {}))
            company_score = self._calculate_company_score(analysis_components.get('company_verification', {}))
            web_score = self._calculate_web_score(analysis_components.get('web_intelligence', {}))
            source_score = self._calculate_source_score(analysis_components.get('source_analysis', {}))
            red_flag_score = self._calculate_red_flag_score(analysis_components.get('red_flag_analysis', {}))

            # Calculate weighted overall score
            component_scores = {
                'content_authenticity': content_score,
                'company_legitimacy': company_score,
                'web_intelligence': web_score,
                'posting_source': source_score,
                'red_flag_analysis': red_flag_score
            }

            overall_score = sum(
                score * self.WEIGHT_DISTRIBUTION[component]
                for component, score in component_scores.items()
            )

            # Determine trust level and recommendations
            trust_level = self._determine_trust_level(overall_score)
            risk_assessment = self._assess_risk_level(overall_score)
            recommendations = self._generate_recommendations(overall_score, analysis_components)
            next_steps = self._generate_next_steps(overall_score, analysis_components)

            trust_score_result = {
                'overall_trust_score': round(overall_score, 1),
                'trust_level': trust_level,
                'risk_assessment': risk_assessment,
                'component_breakdown': {
                    component: {
                        'score': round(score, 1),
                        'weight': self.WEIGHT_DISTRIBUTION[component],
                        'contribution': round(score * self.WEIGHT_DISTRIBUTION[component], 1)
                    }
                    for component, score in component_scores.items()
                },
                'recommendations': recommendations,
                'next_steps': next_steps,
                'analysis_summary': self._generate_analysis_summary(overall_score, component_scores),
                'calculation_timestamp': datetime.now().isoformat()
            }

            logger.info(f"Job trust score calculated: {overall_score:.1f}%")
            return trust_score_result

        except Exception as e:
            logger.error(f"Trust score calculation failed: {str(e)}")
            return self._create_fallback_score(str(e))

    def _calculate_content_score(self, content_analysis: Dict[str, Any]) -> float:
        """Calculate score based on content analysis"""
        if not content_analysis:
            return 50.0  # Neutral score if no analysis available

        score = 70.0  # Base score

        # AI authenticity analysis
        ai_probability = content_analysis.get('ai_probability', 0)
        if ai_probability < 30:
            score += 20  # Likely human-written
        elif ai_probability > 70:
            score -= 25  # Likely AI-generated (suspicious for job postings)

        # Job description quality
        job_description = content_analysis.get('job_description', '')
        if len(job_description) > 200:
            score += 10  # Detailed description
        elif len(job_description) < 50:
            score -= 15  # Too brief/vague

        # Requirements analysis
        requirements = content_analysis.get('requirements', [])
        if len(requirements) >= 3:
            score += 5  # Detailed requirements
        elif len(requirements) == 0:
            score -= 10  # No clear requirements

        # Red flag keywords
        red_flags = content_analysis.get('red_flag_keywords', [])
        score -= min(len(red_flags) * 5, 30)  # Penalty for red flags

        # Salary realism
        salary_info = content_analysis.get('salary_range', {})
        if salary_info.get('is_suspicious', False):
            score -= 20  # Unrealistic salary promises
        elif salary_info.get('found', False):
            score += 5  # Has salary information

        return max(0, min(100, score))

    def _calculate_company_score(self, company_verification: Dict[str, Any]) -> float:
        """Calculate score based on company verification"""
        if not company_verification:
            return 40.0  # Lower neutral score for missing company info

        # Use the calculated legitimacy score from company verification
        legitimacy_score = company_verification.get('overall_legitimacy_score', 50.0)

        # Adjust based on specific factors
        score = legitimacy_score

        # Green flags boost
        green_flags = company_verification.get('green_flags', [])
        score += min(len(green_flags) * 3, 15)

        # Red flags penalty
        red_flags = company_verification.get('red_flags', [])
        score -= min(len(red_flags) * 5, 25)

        return max(0, min(100, score))

    def _calculate_web_score(self, web_intelligence: Dict[str, Any]) -> float:
        """Calculate score based on web intelligence"""
        if not web_intelligence:
            return 45.0  # Lower neutral score for missing web analysis

        # Use the calculated web credibility score
        web_credibility = web_intelligence.get('overall_web_credibility', 50.0)

        # Adjust based on specific findings
        score = web_credibility

        # Credibility factors boost
        credibility_factors = web_intelligence.get('credibility_factors', [])
        score += min(len(credibility_factors) * 2, 10)

        # Warning signs penalty
        warning_signs = web_intelligence.get('warning_signs', [])
        score -= min(len(warning_signs) * 4, 20)

        return max(0, min(100, score))

    def _calculate_source_score(self, source_analysis: Dict[str, Any]) -> float:
        """Calculate score based on posting source"""
        if not source_analysis:
            return 50.0  # Neutral if no source analysis

        score = 50.0  # Base score

        # Check extraction method
        extraction_method = source_analysis.get('extraction_method', '')
        if extraction_method == 'web_scraping':
            # URL-based posting
            domain_credibility = source_analysis.get('domain_credibility', 0)
            score = domain_credibility

            if source_analysis.get('is_legitimate_job_board', False):
                score = 90.0  # High score for legitimate job boards
        elif extraction_method in ['pdf_text', 'ocr_image']:
            # File-based posting - more neutral
            score = 60.0

        return max(0, min(100, score))

    def _calculate_red_flag_score(self, red_flag_analysis: Dict[str, Any]) -> float:
        """Calculate score based on red flag analysis (inverse - fewer red flags = higher score)"""
        if not red_flag_analysis:
            return 70.0  # Neutral-positive if no analysis

        score = 100.0  # Start with perfect score

        # Content red flags
        content_red_flags = red_flag_analysis.get('content_red_flags', [])
        score -= min(len(content_red_flags) * 8, 40)

        # Company red flags
        company_red_flags = red_flag_analysis.get('company_red_flags', [])
        score -= min(len(company_red_flags) * 10, 40)

        # Web red flags
        web_red_flags = red_flag_analysis.get('web_red_flags', [])
        score -= min(len(web_red_flags) * 6, 30)

        # Scam pattern matches
        scam_patterns = red_flag_analysis.get('scam_pattern_matches', [])
        score -= min(len(scam_patterns) * 15, 60)

        return max(0, min(100, score))

    def _determine_trust_level(self, overall_score: float) -> str:
        """Determine trust level based on overall score"""
        if overall_score >= 85:
            return "Very High Trust - Highly Likely Legitimate"
        elif overall_score >= 70:
            return "High Trust - Likely Legitimate"
        elif overall_score >= 55:
            return "Moderate Trust - Proceed with Caution"
        elif overall_score >= 35:
            return "Low Trust - Exercise Significant Caution"
        else:
            return "Very Low Trust - High Risk of Scam"

    def _assess_risk_level(self, overall_score: float) -> str:
        """Assess risk level for job seekers"""
        if overall_score >= 80:
            return "LOW RISK - Safe to apply with standard precautions"
        elif overall_score >= 65:
            return "LOW-MODERATE RISK - Verify company details before applying"
        elif overall_score >= 50:
            return "MODERATE RISK - Research thoroughly and ask detailed questions"
        elif overall_score >= 30:
            return "HIGH RISK - Multiple warning signs detected"
        else:
            return "CRITICAL RISK - Strong scam indicators present"

    def _generate_recommendations(self, overall_score: float, analysis_components: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on trust score"""
        recommendations = []

        if overall_score >= 75:
            recommendations.extend([
                "✅ Job posting appears legitimate and trustworthy",
                "📝 Proceed with standard application process",
                "🔍 Still verify company details during interview process",
                "💼 Ask for clear job description and expectations"
            ])
        elif overall_score >= 55:
            recommendations.extend([
                "⚠️ Exercise moderate caution when applying",
                "🔍 Research the company thoroughly before applying",
                "📞 Verify company contact information independently",
                "💰 Be cautious of any requests for upfront payments",
                "📋 Ask detailed questions about the role and company"
            ])
        elif overall_score >= 35:
            recommendations.extend([
                "🚨 HIGH CAUTION - Multiple warning signs detected",
                "🔍 Thoroughly investigate company legitimacy",
                "📞 Contact company through official channels only",
                "💳 Never provide personal financial information",
                "🤝 Insist on video/phone interview before proceeding",
                "📄 Request official company documentation"
            ])
        else:
            recommendations.extend([
                "❌ AVOID - Strong indicators of fraudulent posting",
                "🚫 Do not provide any personal information",
                "🚫 Do not send money or pay any fees",
                "📢 Consider reporting as potential scam",
                "🔍 Look for legitimate opportunities elsewhere"
            ])

        # Add specific recommendations based on analysis
        content_analysis = analysis_components.get('content_analysis', {})
        if content_analysis.get('red_flag_keywords'):
            recommendations.append("⚠️ Job posting contains suspicious keywords - investigate further")

        company_verification = analysis_components.get('company_verification', {})
        if company_verification.get('red_flags'):
            recommendations.append("🏢 Company verification raised concerns - verify through official channels")

        return recommendations

    def _generate_next_steps(self, overall_score: float, analysis_components: Dict[str, Any]) -> List[str]:
        """Generate specific next steps based on analysis"""
        next_steps = []

        if overall_score >= 70:
            next_steps.extend([
                "1. Prepare a tailored resume and cover letter",
                "2. Research the company's recent news and developments",
                "3. Apply through official company website or job board",
                "4. Follow up appropriately after application"
            ])
        elif overall_score >= 50:
            next_steps.extend([
                "1. Verify company exists through independent research",
                "2. Check company reviews on Glassdoor or similar sites",
                "3. Look up company leadership on LinkedIn",
                "4. Apply only if verification checks pass",
                "5. Be prepared with questions about company legitimacy"
            ])
        else:
            next_steps.extend([
                "1. Do NOT apply to this position",
                "2. Research legitimate companies in your field",
                "3. Use established job boards for job searching",
                "4. Report suspicious posting if on legitimate platform",
                "5. Continue job search with verified opportunities"
            ])

        return next_steps

    def _generate_analysis_summary(self, overall_score: float, component_scores: Dict[str, float]) -> str:
        """Generate human-readable analysis summary"""

        # Find strongest and weakest components
        strongest_component = max(component_scores.items(), key=lambda x: x[1])
        weakest_component = min(component_scores.items(), key=lambda x: x[1])

        component_names = {
            'content_authenticity': 'job posting content',
            'company_legitimacy': 'company verification',
            'web_intelligence': 'web presence',
            'posting_source': 'posting source',
            'red_flag_analysis': 'scam detection'
        }

        summary = f"Overall trust score: {overall_score:.1f}%. "

        if overall_score >= 75:
            summary += f"This job posting shows strong legitimacy indicators, particularly in {component_names[strongest_component[0]]} ({strongest_component[1]:.1f}%). "
        elif overall_score >= 50:
            summary += f"This job posting shows mixed signals. Strong performance in {component_names[strongest_component[0]]} ({strongest_component[1]:.1f}%) but concerns in {component_names[weakest_component[0]]} ({weakest_component[1]:.1f}%). "
        else:
            summary += f"This job posting shows significant warning signs, especially in {component_names[weakest_component[0]]} ({weakest_component[1]:.1f}%). "

        if overall_score >= 70:
            summary += "Proceed with standard job application precautions."
        elif overall_score >= 40:
            summary += "Exercise heightened caution and verify company details thoroughly."
        else:
            summary += "Strong recommendation to avoid this opportunity."

        return summary

    def _create_fallback_score(self, error_message: str) -> Dict[str, Any]:
        """Create fallback trust score when calculation fails"""
        return {
            'overall_trust_score': 0.0,
            'trust_level': "Analysis Failed",
            'risk_assessment': "Unable to assess - analysis error",
            'component_breakdown': {},
            'recommendations': [
                "❌ Trust score calculation failed",
                "🔍 Manual verification strongly recommended",
                "⚠️ Do not proceed without thorough investigation"
            ],
            'next_steps': [
                "1. Manually research the company and job posting",
                "2. Use alternative verification methods",
                "3. Consult with career advisors or trusted sources"
            ],
            'analysis_summary': f"Trust score analysis failed due to: {error_message}",
            'error': error_message,
            'calculation_timestamp': datetime.now().isoformat()
        }
