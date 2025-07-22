import asyncio
import logging
import aiohttp
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class WebIntelligenceEngine:
    """Advanced web intelligence for job posting verification"""

    def __init__(self):
        self.session = None
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        logger.info("WebIntelligenceEngine initialized")

    async def analyze_web_presence(self, company_name: str, company_domain: Optional[str] = None,
                                   job_url: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive web presence analysis"""

        web_intelligence = {
            'company_name': company_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'domain_analysis': {},
            'social_media_presence': {},
            'review_analysis': {},
            'job_board_presence': {},
            'overall_web_credibility': 0.0,
            'credibility_factors': [],
            'warning_signs': []
        }

        try:
            async with aiohttp.ClientSession(
                    headers={'User-Agent': self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                self.session = session

                # Run parallel analysis
                analysis_tasks = [
                    self._analyze_company_domain(company_domain) if company_domain else self._empty_domain_analysis(),
                    self._search_social_media_presence(company_name),
                    self._analyze_company_reviews(company_name),
                    self._check_job_board_presence(company_name),
                    self._analyze_source_url(job_url) if job_url else self._empty_url_analysis()
                ]

                results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

                # Process results
                domain_analysis, social_media, reviews, job_boards, source_url = results

                web_intelligence['domain_analysis'] = domain_analysis if not isinstance(domain_analysis,
                                                                                        Exception) else {
                    'error': str(domain_analysis)}
                web_intelligence['social_media_presence'] = social_media if not isinstance(social_media,
                                                                                           Exception) else {
                    'error': str(social_media)}
                web_intelligence['review_analysis'] = reviews if not isinstance(reviews, Exception) else {
                    'error': str(reviews)}
                web_intelligence['job_board_presence'] = job_boards if not isinstance(job_boards, Exception) else {
                    'error': str(job_boards)}
                web_intelligence['source_url_analysis'] = source_url if not isinstance(source_url, Exception) else {
                    'error': str(source_url)}

                # Calculate overall credibility
                web_intelligence['overall_web_credibility'] = self._calculate_web_credibility(web_intelligence)

                # Generate insights
                web_intelligence['credibility_factors'], web_intelligence[
                    'warning_signs'] = self._generate_web_insights(web_intelligence)

        except Exception as e:
            logger.error(f"Web intelligence analysis failed: {str(e)}")
            web_intelligence['error'] = str(e)

        return web_intelligence

    async def _analyze_company_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze company's official domain"""
        domain_analysis = {
            'domain': domain,
            'is_accessible': False,
            'has_ssl': False,
            'page_quality': 0.0,
            'professional_design': False,
            'contact_info_present': False,
            'careers_page_exists': False,
            'content_quality_score': 0.0,
            'suspicious_elements': []
        }

        try:
            if not domain.startswith(('http://', 'https://')):
                domain = f"https://{domain}"

            async with self.session.get(domain, allow_redirects=True) as response:
                if response.status == 200:
                    domain_analysis['is_accessible'] = True
                    domain_analysis['has_ssl'] = response.url.scheme == 'https'

                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')

                    # Analyze page quality
                    domain_analysis.update(self._analyze_page_quality(soup))

                    # Check for careers page
                    domain_analysis['careers_page_exists'] = await self._check_careers_page(domain)

        except Exception as e:
            logger.warning(f"Domain analysis failed for {domain}: {str(e)}")
            domain_analysis['error'] = str(e)

        return domain_analysis

    def _analyze_page_quality(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze the quality of a webpage"""
        quality_metrics = {
            'professional_design': False,
            'contact_info_present': False,
            'content_quality_score': 0.0,
            'suspicious_elements': []
        }

        # Check for professional elements
        professional_indicators = [
            bool(soup.find('title')),
            bool(soup.find('meta', attrs={'name': 'description'})),
            bool(soup.find('nav')),
            bool(soup.find('footer')),
            len(soup.find_all('img')) > 0,
            bool(soup.find('link', attrs={'rel': 'stylesheet'}))
        ]
        quality_metrics['professional_design'] = sum(professional_indicators) >= 4

        # Check for contact information
        contact_indicators = [
            '@' in soup.get_text(),  # Email
            re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', soup.get_text()),  # Phone
            any(word in soup.get_text().lower() for word in ['contact', 'address', 'phone', 'email'])
        ]
        quality_metrics['contact_info_present'] = any(contact_indicators)

        # Check for suspicious elements
        suspicious_elements = []
        text_content = soup.get_text().lower()
        suspicious_keywords = [
            'get rich quick', 'make money fast', 'work from home guaranteed',
            'no experience necessary', 'earn thousands weekly', 'financial freedom'
        ]

        for keyword in suspicious_keywords:
            if keyword in text_content:
                suspicious_elements.append(keyword)

        quality_metrics['suspicious_elements'] = suspicious_elements

        # Calculate content quality score
        quality_factors = [
            len(soup.get_text()) > 500,  # Sufficient content
            len(soup.find_all('a')) > 5,  # Multiple links
            bool(soup.find('h1')),  # Has main heading
            len(soup.find_all(['h2', 'h3'])) > 0,  # Has subheadings
            len(suspicious_elements) == 0  # No suspicious content
        ]
        quality_metrics['content_quality_score'] = sum(quality_factors) / len(quality_factors) * 100

        return quality_metrics

    async def _check_careers_page(self, base_domain: str) -> bool:
        """Check if company has a careers page"""
        careers_paths = ['/careers', '/jobs', '/career', '/employment', '/join-us', '/opportunities']

        for path in careers_paths:
            try:
                careers_url = urljoin(base_domain, path)
                async with self.session.get(careers_url) as response:
                    if response.status == 200:
                        return True
            except:
                continue

        return False

    async def _search_social_media_presence(self, company_name: str) -> Dict[str, Any]:
        """Analyze social media presence indicators"""
        social_media = {
            'estimated_linkedin_presence': False,
            'estimated_facebook_presence': False,
            'estimated_twitter_presence': False,
            'social_media_score': 0.0,
            'analysis_method': 'heuristic_estimation'
        }

        # Heuristic analysis based on company name characteristics
        # In production, this would use actual social media APIs

        company_lower = company_name.lower()

        # Estimate LinkedIn presence based on company name professionalism
        linkedin_indicators = [
            any(suffix in company_lower for suffix in ['inc', 'corp', 'llc', 'ltd', 'company']),
            len(company_name.split()) >= 2,
            not any(suspicious in company_lower for suspicious in ['home business', 'easy money', 'work from home']),
            len(company_name) > 5
        ]
        social_media['estimated_linkedin_presence'] = sum(linkedin_indicators) >= 3

        # Estimate other social media presence
        if social_media['estimated_linkedin_presence']:
            social_media['estimated_facebook_presence'] = True
            social_media['estimated_twitter_presence'] = True

        # Calculate social media score
        presence_score = sum([
            social_media['estimated_linkedin_presence'],
            social_media['estimated_facebook_presence'],
            social_media['estimated_twitter_presence']
        ]) / 3 * 100

        social_media['social_media_score'] = presence_score

        return social_media

    async def _analyze_company_reviews(self, company_name: str) -> Dict[str, Any]:
        """Analyze company reviews and reputation"""
        review_analysis = {
            'review_availability': 'unknown',
            'estimated_rating': 0.0,
            'review_count_estimate': 0,
            'reputation_indicators': [],
            'warning_indicators': [],
            'analysis_method': 'pattern_based_estimation'
        }

        # Pattern-based analysis for review likelihood
        company_lower = company_name.lower()

        # Indicators that suggest company might have reviews
        review_likelihood_factors = [
            any(suffix in company_lower for suffix in ['inc', 'corp', 'llc', 'ltd']),
            any(industry in company_lower for industry in ['tech', 'software', 'consulting', 'services']),
            len(company_name.split()) <= 4,  # Not overly complex name
            not any(suspicious in company_lower for suspicious in ['home business', 'easy', 'quick', 'fast'])
        ]

        likelihood_score = sum(review_likelihood_factors) / len(review_likelihood_factors)

        if likelihood_score >= 0.7:
            review_analysis['review_availability'] = 'likely_available'
            review_analysis['estimated_rating'] = 3.5 + (likelihood_score - 0.7) * 5  # 3.5-5.0 range
            review_analysis['review_count_estimate'] = int(likelihood_score * 100)
            review_analysis['reputation_indicators'] = ['Professional company name', 'Industry recognition likely']
        elif likelihood_score >= 0.4:
            review_analysis['review_availability'] = 'possibly_available'
            review_analysis['estimated_rating'] = 2.5 + likelihood_score * 2  # 2.5-4.5 range
            review_analysis['review_count_estimate'] = int(likelihood_score * 50)
        else:
            review_analysis['review_availability'] = 'unlikely'
            review_analysis['estimated_rating'] = likelihood_score * 3  # 0-2.1 range
            review_analysis['warning_indicators'] = ['Company name has suspicious characteristics']

        return review_analysis

    async def _check_job_board_presence(self, company_name: str) -> Dict[str, Any]:
        """Analyze presence on legitimate job boards"""
        job_board_presence = {
            'likely_on_major_boards': False,
            'estimated_job_count': 0,
            'board_credibility_score': 0.0,
            'presence_indicators': []
        }

        # Estimate job board presence based on company characteristics
        company_lower = company_name.lower()

        presence_indicators = [
            any(suffix in company_lower for suffix in ['inc', 'corp', 'llc', 'ltd', 'company']),
            any(size_indicator in company_lower for size_indicator in
                ['group', 'systems', 'solutions', 'technologies']),
            len(company_name) >= 5,
            not any(red_flag in company_lower for red_flag in
                    ['home business', 'easy money', 'work from home', 'be your own boss'])
        ]

        presence_score = sum(presence_indicators) / len(presence_indicators)

        job_board_presence['likely_on_major_boards'] = presence_score >= 0.6
        job_board_presence['estimated_job_count'] = int(presence_score * 25)  # 0-25 estimated jobs
        job_board_presence['board_credibility_score'] = presence_score * 100

        if presence_score >= 0.8:
            job_board_presence['presence_indicators'] = ['Professional company profile', 'Multiple job listings likely']
        elif presence_score >= 0.5:
            job_board_presence['presence_indicators'] = ['Some professional indicators']
        else:
            job_board_presence['presence_indicators'] = ['Limited professional presence indicators']

        return job_board_presence

    async def _analyze_source_url(self, job_url: str) -> Dict[str, Any]:
        """Analyze the source URL of the job posting"""
        url_analysis = {
            'source_url': job_url,
            'domain_credibility': 0.0,
            'is_legitimate_job_board': False,
            'url_structure_quality': 0.0,
            'security_indicators': {},
            'credibility_factors': [],
            'warning_signs': []
        }

        try:
            parsed_url = urlparse(job_url)
            domain = parsed_url.netloc.lower()

            # Check against known legitimate job boards
            legitimate_job_boards = [
                'indeed.com', 'linkedin.com', 'glassdoor.com', 'monster.com',
                'careerbuilder.com', 'ziprecruiter.com', 'simplyhired.com',
                'dice.com', 'craigslist.org', 'upwork.com', 'freelancer.com'
            ]

            url_analysis['is_legitimate_job_board'] = any(board in domain for board in legitimate_job_boards)

            # Analyze URL structure quality
            url_quality_factors = [
                parsed_url.scheme == 'https',  # HTTPS
                len(parsed_url.path) > 1,  # Has meaningful path
                not any(suspicious in domain for suspicious in ['bit.ly', 'tinyurl', 'goo.gl']),  # Not shortened URL
                '.' in domain,  # Proper domain format
                len(domain) > 4  # Reasonable domain length
            ]

            url_analysis['url_structure_quality'] = sum(url_quality_factors) / len(url_quality_factors) * 100

            # Security indicators
            url_analysis['security_indicators'] = {
                'uses_https': parsed_url.scheme == 'https',
                'has_suspicious_subdomains': len(parsed_url.netloc.split('.')) > 3,
                'contains_ip_address': re.match(r'^\d+\.\d+\.\d+\.\d+', parsed_url.netloc) is not None
            }

            # Calculate domain credibility
            credibility_factors = []
            warning_signs = []

            if url_analysis['is_legitimate_job_board']:
                url_analysis['domain_credibility'] = 90.0
                credibility_factors.append("Posted on legitimate job board")
            elif parsed_url.scheme == 'https':
                url_analysis['domain_credibility'] = 60.0
                credibility_factors.append("Uses secure HTTPS connection")
            else:
                url_analysis['domain_credibility'] = 30.0
                warning_signs.append("Uses insecure HTTP connection")

            if url_analysis['security_indicators']['contains_ip_address']:
                warning_signs.append("URL contains IP address instead of domain name")
                url_analysis['domain_credibility'] -= 20

            url_analysis['credibility_factors'] = credibility_factors
            url_analysis['warning_signs'] = warning_signs

        except Exception as e:
            logger.error(f"URL analysis failed: {str(e)}")
            url_analysis['error'] = str(e)

        return url_analysis

    def _calculate_web_credibility(self, web_intelligence: Dict[str, Any]) -> float:
        """Calculate overall web credibility score"""
        score = 0.0
        max_score = 100.0

        # Domain analysis (35% weight)
        domain_analysis = web_intelligence.get('domain_analysis', {})
        if not domain_analysis.get('error'):
            if domain_analysis.get('is_accessible', False):
                score += 12
            if domain_analysis.get('has_ssl', False):
                score += 8
            if domain_analysis.get('professional_design', False):
                score += 10
            if domain_analysis.get('careers_page_exists', False):
                score += 5

        # Social media presence (20% weight)
        social_media = web_intelligence.get('social_media_presence', {})
        if not social_media.get('error'):
            social_score = social_media.get('social_media_score', 0)
            score += (social_score / 100) * 20

        # Review analysis (20% weight)
        review_analysis = web_intelligence.get('review_analysis', {})
        if not review_analysis.get('error'):
            if review_analysis.get('review_availability') == 'likely_available':
                score += 15
            elif review_analysis.get('review_availability') == 'possibly_available':
                score += 10
            if review_analysis.get('estimated_rating', 0) > 3.5:
                score += 5

        # Job board presence (15% weight)
        job_board_presence = web_intelligence.get('job_board_presence', {})
        if not job_board_presence.get('error'):
            if job_board_presence.get('likely_on_major_boards', False):
                score += 10
            credibility_score = job_board_presence.get('board_credibility_score', 0)
            score += (credibility_score / 100) * 5

        # Source URL analysis (10% weight)
        source_url_analysis = web_intelligence.get('source_url_analysis', {})
        if not source_url_analysis.get('error'):
            if source_url_analysis.get('is_legitimate_job_board', False):
                score += 8
            else:
                domain_cred = source_url_analysis.get('domain_credibility', 0)
                score += (domain_cred / 100) * 2

        return min(score, max_score)

    def _generate_web_insights(self, web_intelligence: Dict[str, Any]) -> tuple:
        """Generate credibility factors and warning signs"""
        credibility_factors = []
        warning_signs = []

        # Analyze domain
        domain_analysis = web_intelligence.get('domain_analysis', {})
        if domain_analysis.get('professional_design'):
            credibility_factors.append("Company website shows professional design")
        if domain_analysis.get('careers_page_exists'):
            credibility_factors.append("Company has dedicated careers section")
        if domain_analysis.get('suspicious_elements'):
            warning_signs.append(
                f"Website contains suspicious keywords: {', '.join(domain_analysis['suspicious_elements'])}")

        # Analyze social media
        social_media = web_intelligence.get('social_media_presence', {})
        if social_media.get('estimated_linkedin_presence'):
            credibility_factors.append("Company likely has LinkedIn presence")

        # Analyze reviews
        review_analysis = web_intelligence.get('review_analysis', {})
        if review_analysis.get('warning_indicators'):
            warning_signs.extend(review_analysis['warning_indicators'])

        # Analyze source URL
        source_url_analysis = web_intelligence.get('source_url_analysis', {})
        if source_url_analysis.get('credibility_factors'):
            credibility_factors.extend(source_url_analysis['credibility_factors'])
        if source_url_analysis.get('warning_signs'):
            warning_signs.extend(source_url_analysis['warning_signs'])

        return credibility_factors, warning_signs

    async def _empty_domain_analysis(self) -> Dict[str, Any]:
        """Return empty domain analysis when no domain provided"""
        return {
            'domain': None,
            'is_accessible': False,
            'has_ssl': False,
            'page_quality': 0.0,
            'professional_design': False,
            'contact_info_present': False,
            'careers_page_exists': False,
            'content_quality_score': 0.0,
            'suspicious_elements': [],
            'note': 'No domain provided for analysis'
        }

    async def _empty_url_analysis(self) -> Dict[str, Any]:
        """Return empty URL analysis when no URL provided"""
        return {
            'source_url': None,
            'domain_credibility': 0.0,
            'is_legitimate_job_board': False,
            'url_structure_quality': 0.0,
            'security_indicators': {},
            'credibility_factors': [],
            'warning_signs': [],
            'note': 'No source URL provided for analysis'
        }
