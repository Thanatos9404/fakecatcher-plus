import asyncio
import logging
from typing import Dict, Any, Optional, Union, List
from fastapi import UploadFile
from datetime import datetime

from .content_extractor import JobContentExtractor
from .company_verifier import CompanyVerifier
from .web_intelligence import WebIntelligenceEngine
from .job_trust_score import JobTrustScoreCalculator
from ..ai_detection.hf_client import HuggingFaceAIClient

logger = logging.getLogger(__name__)


class JobPostingAnalyzer:
    """Main analyzer for job posting authenticity verification"""

    def __init__(self):
        self.content_extractor = JobContentExtractor()
        self.company_verifier = CompanyVerifier()
        self.web_intelligence = WebIntelligenceEngine()
        self.trust_calculator = JobTrustScoreCalculator()
        self.ai_client = HuggingFaceAIClient()

        logger.info("JobPostingAnalyzer initialized with all components")

    async def analyze_job_posting(self, input_type: str, input_data: Union[UploadFile, str]) -> Dict[str, Any]:
        """
        Comprehensive job posting analysis

        Args:
            input_type: 'image', 'pdf', or 'url'
            input_data: UploadFile for image/pdf, string URL for url
        """

        analysis_start_time = datetime.now()

        # Initialize analysis result structure
        analysis_result = {
            'analysis_id': f"job_{int(analysis_start_time.timestamp())}",
            'input_type': input_type,
            'analysis_timestamp': analysis_start_time.isoformat(),
            'status': 'in_progress',
            'job_content': {},
            'content_analysis': {},
            'company_verification': {},
            'web_intelligence': {},
            'trust_score': {},
            'processing_details': {
                'content_extraction_successful': False,
                'ai_analysis_successful': False,
                'company_verification_successful': False,
                'web_intelligence_successful': False,
                'trust_calculation_successful': False
            },
            'errors': [],
            'warnings': []
        }

        try:
            # Phase 1: Content Extraction
            logger.info(f"Starting job analysis for input type: {input_type}")
            job_content = await self._extract_job_content(input_type, input_data)
            analysis_result['job_content'] = job_content
            analysis_result['processing_details']['content_extraction_successful'] = True

            # Phase 2: AI Content Analysis
            if job_content.get('raw_text'):
                content_analysis = await self._analyze_job_content(job_content)
                analysis_result['content_analysis'] = content_analysis
                analysis_result['processing_details']['ai_analysis_successful'] = True

            # Phase 3: Company Verification
            company_name = job_content.get('company_name')
            company_domain = job_content.get('domain') or self._extract_domain_from_contact(
                job_content.get('contact_info', {}))

            if company_name:
                company_verification = await self.company_verifier.verify_company(company_name, company_domain)
                analysis_result['company_verification'] = company_verification
                analysis_result['processing_details']['company_verification_successful'] = True

            # Phase 4: Web Intelligence
            source_url = job_content.get('source_url')
            web_intelligence = await self.web_intelligence.analyze_web_presence(
                company_name or "Unknown Company",
                company_domain,
                source_url
            )
            analysis_result['web_intelligence'] = web_intelligence
            analysis_result['processing_details']['web_intelligence_successful'] = True

            # Phase 5: Trust Score Calculation
            trust_score = self.trust_calculator.calculate_job_trust_score({
                'content_analysis': analysis_result['content_analysis'],
                'company_verification': analysis_result['company_verification'],
                'web_intelligence': analysis_result['web_intelligence'],
                'source_analysis': {
                    'extraction_method': job_content.get('extraction_method'),
                    'domain_credibility': web_intelligence.get('source_url_analysis', {}).get('domain_credibility', 0),
                    'is_legitimate_job_board': web_intelligence.get('source_url_analysis', {}).get(
                        'is_legitimate_job_board', False)
                },
                'red_flag_analysis': self._compile_red_flags(analysis_result)
            })
            analysis_result['trust_score'] = trust_score
            analysis_result['processing_details']['trust_calculation_successful'] = True

            # Finalize analysis
            analysis_result['status'] = 'completed'
            analysis_result['processing_time_seconds'] = (datetime.now() - analysis_start_time).total_seconds()

            logger.info(
                f"Job analysis completed successfully in {analysis_result['processing_time_seconds']:.2f} seconds")

        except Exception as e:
            logger.error(f"Job analysis failed: {str(e)}")
            analysis_result['status'] = 'failed'
            analysis_result['errors'].append(str(e))
            analysis_result['processing_time_seconds'] = (datetime.now() - analysis_start_time).total_seconds()

        return analysis_result

    async def _extract_job_content(self, input_type: str, input_data: Union[UploadFile, str]) -> Dict[str, Any]:
        """Extract job content based on input type"""

        try:
            if input_type == 'image':
                return await self.content_extractor.extract_from_image(input_data)
            elif input_type == 'pdf':
                return await self.content_extractor.extract_from_pdf(input_data)
            elif input_type == 'url':
                return await self.content_extractor.extract_from_url(input_data)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")

        except Exception as e:
            logger.error(f"Content extraction failed for {input_type}: {str(e)}")
            raise Exception(f"Failed to extract job content: {str(e)}")

    async def _analyze_job_content(self, job_content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job content using AI and pattern detection"""

        content_analysis = {
            'ai_analysis': {},
            'pattern_analysis': {},
            'quality_assessment': {},
            'red_flag_detection': {}
        }

        raw_text = job_content.get('raw_text', '')

        try:
            # AI analysis using existing Hugging Face client
            ai_analysis = await self.ai_client.detect_ai_generated_content(raw_text)
            content_analysis['ai_analysis'] = ai_analysis

            # Pattern analysis specific to job postings
            pattern_analysis = self._analyze_job_patterns(job_content)
            content_analysis['pattern_analysis'] = pattern_analysis

            # Quality assessment
            quality_assessment = self._assess_content_quality(job_content)
            content_analysis['quality_assessment'] = quality_assessment

            # Red flag detection
            red_flag_detection = self._detect_job_red_flags(job_content)
            content_analysis['red_flag_detection'] = red_flag_detection

            # Overall content score
            content_analysis['overall_content_score'] = self._calculate_content_score(content_analysis)

        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            content_analysis['error'] = str(e)

        return content_analysis

    def _analyze_job_patterns(self, job_content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns specific to job postings"""

        pattern_analysis = {
            'salary_realism': self._analyze_salary_realism(job_content.get('salary_range', {})),
            'requirement_consistency': self._analyze_requirements_consistency(job_content.get('requirements', [])),
            'description_quality': self._analyze_description_quality(job_content.get('job_description', '')),
            'contact_legitimacy': self._analyze_contact_legitimacy(job_content.get('contact_info', {})),
            'urgency_indicators': self._detect_urgency_tactics(job_content.get('raw_text', '')),
            'vagueness_score': self._calculate_vagueness_score(job_content)
        }

        return pattern_analysis

    def _analyze_salary_realism(self, salary_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze if salary information is realistic"""

        salary_analysis = {
            'has_salary_info': salary_info.get('found', False),
            'is_realistic': True,
            'suspicion_level': 'low',
            'warnings': []
        }

        if salary_info.get('is_suspicious', False):
            salary_analysis['is_realistic'] = False
            salary_analysis['suspicion_level'] = 'high'
            salary_analysis['warnings'].append("Salary appears unrealistically high")

        raw_text = salary_info.get('raw_text', '')
        if raw_text:
            suspicious_salary_phrases = [
                'make thousands weekly', 'unlimited earning potential',
                'guaranteed income', 'earn up to $5000/week'
            ]

            for phrase in suspicious_salary_phrases:
                if phrase in raw_text.lower():
                    salary_analysis['warnings'].append(f"Contains suspicious phrase: {phrase}")
                    salary_analysis['suspicion_level'] = 'high'

        return salary_analysis

    def _analyze_requirements_consistency(self, requirements: List[str]) -> Dict[str, Any]:
        """Analyze consistency and realism of job requirements"""

        consistency_analysis = {
            'has_requirements': len(requirements) > 0,
            'requirement_count': len(requirements),
            'specificity_score': 0.0,
            'consistency_issues': []
        }

        if not requirements:
            consistency_analysis['consistency_issues'].append("No specific requirements listed")
            return consistency_analysis

        # Analyze specificity
        specific_indicators = ['years of experience', 'degree', 'certification', 'specific software',
                               'programming language']
        vague_indicators = ['good communication', 'team player', 'motivated', 'enthusiastic']

        specific_count = 0
        vague_count = 0

        for req in requirements:
            req_lower = req.lower()
            if any(indicator in req_lower for indicator in specific_indicators):
                specific_count += 1
            if any(indicator in req_lower for indicator in vague_indicators):
                vague_count += 1

        if len(requirements) > 0:
            consistency_analysis['specificity_score'] = (specific_count / len(requirements)) * 100

        if vague_count > specific_count:
            consistency_analysis['consistency_issues'].append("Requirements are too vague")

        return consistency_analysis

    def _analyze_description_quality(self, job_description: str) -> Dict[str, Any]:
        """Analyze quality of job description"""

        quality_analysis = {
            'length_appropriate': False,
            'detail_level': 'insufficient',
            'professional_language': True,
            'clarity_score': 0.0,
            'quality_issues': []
        }

        if not job_description:
            quality_analysis['quality_issues'].append("No job description provided")
            return quality_analysis

        # Length analysis
        word_count = len(job_description.split())
        if word_count > 50:
            quality_analysis['length_appropriate'] = True
            if word_count > 100:
                quality_analysis['detail_level'] = 'adequate'
            if word_count > 200:
                quality_analysis['detail_level'] = 'detailed'
        else:
            quality_analysis['quality_issues'].append("Job description is too brief")

        # Professional language check
        unprofessional_indicators = ['easy money', 'get rich', 'no work required', '!!!', 'URGENT', 'ASAP']
        for indicator in unprofessional_indicators:
            if indicator.lower() in job_description.lower():
                quality_analysis['professional_language'] = False
                quality_analysis['quality_issues'].append(f"Contains unprofessional language: {indicator}")

        # Clarity score (simplified)
        sentences = job_description.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if avg_sentence_length < 30:  # Reasonable sentence length
            quality_analysis['clarity_score'] = min(90, avg_sentence_length * 3)
        else:
            quality_analysis['clarity_score'] = max(30, 90 - (avg_sentence_length - 30))

        return quality_analysis

    def _analyze_contact_legitimacy(self, contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze legitimacy of contact information"""

        contact_analysis = {
            'has_email': bool(contact_info.get('email')),
            'has_phone': bool(contact_info.get('phone')),
            'has_website': bool(contact_info.get('website')),
            'email_professional': False,
            'contact_completeness_score': 0.0,
            'legitimacy_indicators': [],
            'red_flags': []
        }

        # Email analysis
        email = contact_info.get('email', '')
        if email:
            # Check for professional email domains
            professional_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com', '.org', '.edu']
            suspicious_domains = ['tempmail', '10minutemail', 'guerrillamail']

            if any(domain in email for domain in professional_domains):
                contact_analysis['email_professional'] = True
                contact_analysis['legitimacy_indicators'].append("Professional email domain")

            if any(domain in email for domain in suspicious_domains):
                contact_analysis['red_flags'].append("Suspicious/temporary email domain")

        # Calculate completeness score
        contact_fields = [contact_info.get('email'), contact_info.get('phone'), contact_info.get('website')]
        contact_analysis['contact_completeness_score'] = (sum(1 for field in contact_fields if field) / len(
            contact_fields)) * 100

        return contact_analysis

    def _detect_urgency_tactics(self, raw_text: str) -> Dict[str, Any]:
        """Detect high-pressure urgency tactics"""

        urgency_analysis = {
            'urgency_level': 'low',
            'urgency_phrases': [],
            'pressure_tactics_detected': False
        }

        urgency_indicators = [
            'urgent hiring', 'immediate start', 'apply today', 'limited positions',
            'act now', 'don\'t miss out', 'limited time', 'hire immediately',
            'start asap', 'urgent need', 'apply now'
        ]

        text_lower = raw_text.lower()
        found_indicators = [indicator for indicator in urgency_indicators if indicator in text_lower]

        urgency_analysis['urgency_phrases'] = found_indicators

        if len(found_indicators) >= 3:
            urgency_analysis['urgency_level'] = 'high'
            urgency_analysis['pressure_tactics_detected'] = True
        elif len(found_indicators) >= 1:
            urgency_analysis['urgency_level'] = 'moderate'

        return urgency_analysis

    def _calculate_vagueness_score(self, job_content: Dict[str, Any]) -> float:
        """Calculate how vague the job posting is"""

        vagueness_factors = []

        # Job title vagueness
        job_title = job_content.get('job_title', '')
        if job_title:
            vague_titles = ['data entry', 'work from home', 'general assistant', 'various positions']
            if any(vague in job_title.lower() for vague in vague_titles):
                vagueness_factors.append(20)
        else:
            vagueness_factors.append(25)  # No title is very vague

        # Company name vagueness
        company_name = job_content.get('company_name', '')
        if not company_name or len(company_name) < 3:
            vagueness_factors.append(20)

        # Job description vagueness
        job_description = job_content.get('job_description', '')
        if len(job_description.split()) < 50:
            vagueness_factors.append(15)

        # Requirements vagueness
        requirements = job_content.get('requirements', [])
        if len(requirements) < 2:
            vagueness_factors.append(15)

        # Location vagueness
        location = job_content.get('location', '')
        if not location or 'remote' in location.lower():
            vagueness_factors.append(10)

        return min(100, sum(vagueness_factors))

    def _assess_content_quality(self, job_content: Dict[str, Any]) -> Dict[str, Any]:
        """Overall content quality assessment"""

        quality_assessment = {
            'completeness_score': 0.0,
            'professionalism_score': 0.0,
            'clarity_score': 0.0,
            'overall_quality_score': 0.0,
            'quality_issues': []
        }

        # Completeness score
        required_fields = ['job_title', 'company_name', 'job_description', 'requirements']
        present_fields = sum(1 for field in required_fields if job_content.get(field))
        quality_assessment['completeness_score'] = (present_fields / len(required_fields)) * 100

        # Professionalism score (based on language and structure)
        raw_text = job_content.get('raw_text', '')
        unprofessional_indicators = ['!!!', 'URGENT', 'easy money', 'get rich', 'work from home guaranteed']
        professional_penalty = sum(
            5 for indicator in unprofessional_indicators if indicator.lower() in raw_text.lower())
        quality_assessment['professionalism_score'] = max(0, 100 - professional_penalty)

        # Clarity score (average of description and requirements clarity)
        desc_clarity = 70 if len(job_content.get('job_description', '').split()) > 50 else 30
        req_clarity = 70 if len(job_content.get('requirements', [])) > 2 else 30
        quality_assessment['clarity_score'] = (desc_clarity + req_clarity) / 2

        # Overall quality score
        quality_assessment['overall_quality_score'] = (
                quality_assessment['completeness_score'] * 0.4 +
                quality_assessment['professionalism_score'] * 0.3 +
                quality_assessment['clarity_score'] * 0.3
        )

        # Identify quality issues
        if quality_assessment['completeness_score'] < 75:
            quality_assessment['quality_issues'].append("Missing important job details")
        if quality_assessment['professionalism_score'] < 70:
            quality_assessment['quality_issues'].append("Unprofessional language detected")
        if quality_assessment['clarity_score'] < 50:
            quality_assessment['quality_issues'].append("Job description lacks clarity")

        return quality_assessment

    def _detect_job_red_flags(self, job_content: Dict[str, Any]) -> Dict[str, Any]:
        """Detect red flags specific to job postings"""

        red_flag_detection = {
            'total_red_flags': 0,
            'critical_red_flags': [],
            'warning_red_flags': [],
            'red_flag_categories': {
                'financial_scam': [],
                'mlm_pyramid': [],
                'data_harvesting': [],
                'fake_company': [],
                'unrealistic_promises': []
            }
        }

        raw_text = job_content.get('raw_text', '').lower()

        # Financial scam indicators
        financial_scams = [
            'pay upfront fee', 'training fee required', 'starter kit cost',
            'wire transfer', 'western union', 'send money', 'processing fee'
        ]
        for scam in financial_scams:
            if scam in raw_text:
                red_flag_detection['red_flag_categories']['financial_scam'].append(scam)
                red_flag_detection['critical_red_flags'].append(f"Financial scam indicator: {scam}")

        # MLM/Pyramid scheme indicators
        mlm_indicators = [
            'unlimited earning potential', 'be your own boss', 'financial freedom',
            'recruit others', 'build your team', 'residual income', 'pyramid', 'mlm'
        ]
        for mlm in mlm_indicators:
            if mlm in raw_text:
                red_flag_detection['red_flag_categories']['mlm_pyramid'].append(mlm)
                red_flag_detection['warning_red_flags'].append(f"MLM/Pyramid indicator: {mlm}")

        # Data harvesting indicators
        data_harvest = [
            'provide ssn', 'social security', 'bank details', 'credit check',
            'background check fee', 'identity verification fee'
        ]
        for harvest in data_harvest:
            if harvest in raw_text:
                red_flag_detection['red_flag_categories']['data_harvesting'].append(harvest)
                red_flag_detection['critical_red_flags'].append(f"Data harvesting: {harvest}")

        # Fake company indicators
        fake_company = [
            'newly established', 'startup opportunity', 'no experience necessary',
            'work from anywhere', 'flexible schedule guaranteed'
        ]
        for fake in fake_company:
            if fake in raw_text:
                red_flag_detection['red_flag_categories']['fake_company'].append(fake)
                red_flag_detection['warning_red_flags'].append(f"Fake company indicator: {fake}")

        # Unrealistic promises
        unrealistic = [
            'guaranteed income', 'make thousands weekly', 'easy money',
            'no work required', 'earn while you sleep', 'get rich quick'
        ]
        for promise in unrealistic:
            if promise in raw_text:
                red_flag_detection['red_flag_categories']['unrealistic_promises'].append(promise)
                red_flag_detection['critical_red_flags'].append(f"Unrealistic promise: {promise}")

        # Calculate total red flags
        red_flag_detection['total_red_flags'] = (
                len(red_flag_detection['critical_red_flags']) +
                len(red_flag_detection['warning_red_flags'])
        )

        return red_flag_detection

    def _calculate_content_score(self, content_analysis: Dict[str, Any]) -> float:
        """Calculate overall content score"""

        # Base score from quality assessment
        base_score = content_analysis.get('quality_assessment', {}).get('overall_quality_score', 50.0)

        # Adjust based on AI analysis
        ai_analysis = content_analysis.get('ai_analysis', {})
        if not ai_analysis.get('fallback_mode', True):
            ai_probability = ai_analysis.get('ai_probability', 0)
            if ai_probability > 70:  # Likely AI-generated job posting is suspicious
                base_score -= 20

        # Adjust based on red flags
        red_flags = content_analysis.get('red_flag_detection', {})
        critical_count = len(red_flags.get('critical_red_flags', []))
        warning_count = len(red_flags.get('warning_red_flags', []))

        base_score -= (critical_count * 15) + (warning_count * 5)

        # Adjust based on pattern analysis
        pattern_analysis = content_analysis.get('pattern_analysis', {})
        if pattern_analysis.get('urgency_indicators', {}).get('pressure_tactics_detected', False):
            base_score -= 10

        vagueness_score = pattern_analysis.get('vagueness_score', 0)
        base_score -= (vagueness_score * 0.2)  # Reduce based on vagueness

        return max(0, min(100, base_score))

    def _compile_red_flags(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compile red flags from all analysis components"""

        compiled_red_flags = {
            'content_red_flags': [],
            'company_red_flags': [],
            'web_red_flags': [],
            'scam_pattern_matches': []
        }

        # Content red flags
        content_red_flags = analysis_result.get('content_analysis', {}).get('red_flag_detection', {})
        compiled_red_flags['content_red_flags'] = (
                content_red_flags.get('critical_red_flags', []) +
                content_red_flags.get('warning_red_flags', [])
        )

        # Company red flags
        company_verification = analysis_result.get('company_verification', {})
        compiled_red_flags['company_red_flags'] = company_verification.get('red_flags', [])

        # Web red flags
        web_intelligence = analysis_result.get('web_intelligence', {})
        compiled_red_flags['web_red_flags'] = web_intelligence.get('warning_signs', [])

        # Scam pattern matches
        for category, patterns in content_red_flags.get('red_flag_categories', {}).items():
            if patterns:
                compiled_red_flags['scam_pattern_matches'].extend([f"{category}: {pattern}" for pattern in patterns])

        return compiled_red_flags

    def _extract_domain_from_contact(self, contact_info: Dict[str, Any]) -> Optional[str]:
        """Extract domain from contact information"""

        email = contact_info.get('email', '')
        if email and '@' in email:
            domain = email.split('@')[1]
            return domain

        website = contact_info.get('website', '')
        if website:
            if website.startswith(('http://', 'https://')):
                from urllib.parse import urlparse
                parsed = urlparse(website)
                return parsed.netloc
            else:
                return website

        return None

    async def health_check(self) -> Dict[str, Any]:
        """Check health of job analyzer components"""

        health_status = {
            'overall_status': 'healthy',
            'components': {
                'content_extractor': 'operational',
                'company_verifier': 'operational',
                'web_intelligence': 'operational',
                'trust_calculator': 'operational',
                'ai_client': 'unknown'
            },
            'capabilities': {
                'image_analysis': True,
                'pdf_analysis': True,
                'url_analysis': True,
                'ai_enhancement': False
            }
        }

        # Check AI client
        try:
            ai_health = await self.ai_client.health_check()
            health_status['components']['ai_client'] = ai_health.get('status', 'unknown')
            health_status['capabilities']['ai_enhancement'] = ai_health.get('api_accessible', False)
        except Exception as e:
            health_status['components']['ai_client'] = f"error: {str(e)}"

        # Determine overall status
        failed_components = [comp for comp, status in health_status['components'].items() if 'error' in str(status)]
        if failed_components:
            health_status['overall_status'] = 'degraded'
            health_status['failed_components'] = failed_components

        return health_status
