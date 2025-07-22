import asyncio
import logging
import aiohttp
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import whois
from datetime import datetime
import socket

logger = logging.getLogger(__name__)


class CompanyVerifier:
    """Verify company legitimacy through multiple sources"""

    def __init__(self):
        self.session = None
        logger.info("CompanyVerifier initialized")

    async def verify_company(self, company_name: str, company_domain: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive company verification"""

        verification_results = {
            'company_name': company_name,
            'company_domain': company_domain,
            'overall_legitimacy_score': 0.0,
            'verification_details': {},
            'red_flags': [],
            'green_flags': [],
            'analysis_timestamp': datetime.now().isoformat()
        }

        try:
            # Run verification checks in parallel
            verification_tasks = [
                self._check_domain_info(company_domain) if company_domain else self._create_empty_result(),
                self._search_company_online(company_name),
                self._check_business_patterns(company_name),
                self._analyze_company_name_quality(company_name),
                self._check_domain_reputation(company_domain) if company_domain else self._create_empty_result()
            ]

            results = await asyncio.gather(*verification_tasks, return_exceptions=True)

            # Process results
            domain_info, online_presence, business_patterns, name_quality, domain_reputation = results

            verification_results['verification_details'] = {
                'domain_analysis': domain_info if not isinstance(domain_info, Exception) else {
                    'error': str(domain_info)},
                'online_presence': online_presence if not isinstance(online_presence, Exception) else {
                    'error': str(online_presence)},
                'business_patterns': business_patterns if not isinstance(business_patterns, Exception) else {
                    'error': str(business_patterns)},
                'name_quality': name_quality if not isinstance(name_quality, Exception) else {
                    'error': str(name_quality)},
                'domain_reputation': domain_reputation if not isinstance(domain_reputation, Exception) else {
                    'error': str(domain_reputation)}
            }

            # Calculate overall legitimacy score
            verification_results['overall_legitimacy_score'] = self._calculate_legitimacy_score(
                verification_results['verification_details'])

            # Determine red and green flags
            verification_results['red_flags'], verification_results['green_flags'] = self._analyze_flags(
                verification_results['verification_details'])

            logger.info(
                f"Company verification completed for {company_name}: {verification_results['overall_legitimacy_score']:.1f}%")

        except Exception as e:
            logger.error(f"Company verification failed: {str(e)}")
            verification_results['error'] = str(e)
            verification_results['overall_legitimacy_score'] = 0.0

        return verification_results

    async def _check_domain_info(self, domain: str) -> Dict[str, Any]:
        """Check domain registration and age"""
        domain_info = {
            'domain': domain,
            'is_registered': False,
            'age_days': 0,
            'registrar': None,
            'creation_date': None,
            'expiration_date': None,
            'is_suspicious': False,
            'registration_country': None,
            'nameservers': [],
            'status': []
        }

        try:
            # Clean domain
            if domain.startswith(('http://', 'https://')):
                domain = urlparse(domain).netloc

            # Remove www prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]

            # Get WHOIS information
            domain_whois = whois.whois(domain)

            if domain_whois:
                domain_info['is_registered'] = True
                domain_info['registrar'] = domain_whois.registrar

                # Handle creation date
                creation_date = domain_whois.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]

                if creation_date:
                    domain_info['creation_date'] = creation_date.isoformat() if hasattr(creation_date,
                                                                                        'isoformat') else str(
                        creation_date)

                    # Calculate domain age
                    if hasattr(creation_date, 'date'):
                        age = (datetime.now().date() - creation_date.date()).days
                        domain_info['age_days'] = age

                        # Flag very new domains (common in scams)
                        if age < 30:
                            domain_info['is_suspicious'] = True
                        elif age < 90:
                            domain_info['is_suspicious'] = False  # Moderately new

                # Handle expiration date
                expiration_date = domain_whois.expiration_date
                if isinstance(expiration_date, list):
                    expiration_date = expiration_date[0]

                if expiration_date:
                    domain_info['expiration_date'] = expiration_date.isoformat() if hasattr(expiration_date,
                                                                                            'isoformat') else str(
                        expiration_date)

                # Additional WHOIS data
                if hasattr(domain_whois, 'country'):
                    domain_info['registration_country'] = domain_whois.country

                if hasattr(domain_whois, 'name_servers'):
                    nameservers = domain_whois.name_servers
                    if nameservers:
                        domain_info['nameservers'] = list(nameservers) if isinstance(nameservers, (list, set)) else [
                            str(nameservers)]

                if hasattr(domain_whois, 'status'):
                    status = domain_whois.status
                    if status:
                        domain_info['status'] = list(status) if isinstance(status, (list, set)) else [str(status)]

        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {str(e)}")
            domain_info['error'] = str(e)

            # Try basic DNS lookup as fallback
            try:
                socket.gethostbyname(domain)
                domain_info['is_registered'] = True
                domain_info['note'] = 'Domain exists but WHOIS data unavailable'
            except socket.gaierror:
                domain_info['note'] = 'Domain does not resolve'

        return domain_info

    async def _check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation and security status"""
        reputation_info = {
            'domain': domain,
            'ssl_certificate': False,
            'security_headers': {},
            'page_accessible': False,
            'redirect_chains': [],
            'suspicious_redirects': False,
            'reputation_score': 50.0
        }

        try:
            if not domain.startswith(('http://', 'https://')):
                # Try HTTPS first
                test_urls = [f"https://{domain}", f"http://{domain}"]
            else:
                test_urls = [domain]

            async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=10),
                    connector=aiohttp.TCPConnector(ssl=False)
            ) as session:

                for url in test_urls:
                    try:
                        async with session.get(url, allow_redirects=True) as response:
                            reputation_info['page_accessible'] = True
                            reputation_info['ssl_certificate'] = url.startswith('https://')

                            # Check for redirect chains
                            if len(response.history) > 0:
                                redirects = [str(resp.url) for resp in response.history]
                                reputation_info['redirect_chains'] = redirects

                                # Check for suspicious redirects
                                if len(redirects) > 3:
                                    reputation_info['suspicious_redirects'] = True

                            # Check security headers
                            headers = response.headers
                            reputation_info['security_headers'] = {
                                'strict_transport_security': 'strict-transport-security' in headers,
                                'content_security_policy': 'content-security-policy' in headers,
                                'x_frame_options': 'x-frame-options' in headers,
                                'x_content_type_options': 'x-content-type-options' in headers
                            }

                            break  # Success, no need to try other URLs

                    except Exception as e:
                        logger.debug(f"Failed to access {url}: {str(e)}")
                        continue

            # Calculate reputation score
            score = 50.0  # Base score

            if reputation_info['page_accessible']:
                score += 20
            if reputation_info['ssl_certificate']:
                score += 15
            if not reputation_info['suspicious_redirects']:
                score += 10

            security_score = sum(reputation_info['security_headers'].values()) / len(
                reputation_info['security_headers']) * 5
            score += security_score

            reputation_info['reputation_score'] = min(100, max(0, score))

        except Exception as e:
            logger.warning(f"Domain reputation check failed for {domain}: {str(e)}")
            reputation_info['error'] = str(e)

        return reputation_info

    async def _search_company_online(self, company_name: str) -> Dict[str, Any]:
        """Search for company presence online using heuristic analysis"""
        online_presence = {
            'search_results_estimated': 0,
            'has_linkedin_likelihood': False,
            'has_glassdoor_likelihood': False,
            'has_official_website_likelihood': False,
            'social_media_presence_score': 0.0,
            'professional_presence_indicators': [],
            'suspicious_indicators': []
        }

        try:
            # Analyze company name patterns to estimate online presence
            name_indicators = self._analyze_company_name_indicators(company_name)
            online_presence.update(name_indicators)

            # Estimate search results based on company characteristics
            online_presence['search_results_estimated'] = self._estimate_search_results(company_name)

            # Calculate social media presence score
            presence_factors = [
                online_presence['has_linkedin_likelihood'],
                online_presence['has_glassdoor_likelihood'],
                online_presence['has_official_website_likelihood']
            ]
            online_presence['social_media_presence_score'] = sum(presence_factors) / len(presence_factors) * 100

        except Exception as e:
            logger.error(f"Online search analysis failed for {company_name}: {str(e)}")
            online_presence['error'] = str(e)

        return online_presence

    def _analyze_company_name_indicators(self, company_name: str) -> Dict[str, Any]:
        """Analyze company name for legitimacy indicators"""
        indicators = {
            'has_corporate_suffix': False,
            'name_length_appropriate': False,
            'contains_suspicious_keywords': False,
            'professional_naming': False,
            'has_linkedin_likelihood': False,
            'has_glassdoor_likelihood': False,
            'has_official_website_likelihood': False,
            'professional_presence_indicators': [],
            'suspicious_indicators': []
        }

        if company_name:
            name_lower = company_name.lower()
            name_words = company_name.split()

            # Check for corporate suffixes
            corporate_suffixes = ['inc', 'corp', 'corporation', 'llc', 'ltd', 'limited', 'company', 'co', 'group',
                                  'solutions', 'technologies', 'systems', 'services', 'consulting', 'enterprises']
            indicators['has_corporate_suffix'] = any(suffix in name_lower for suffix in corporate_suffixes)
            if indicators['has_corporate_suffix']:
                indicators['professional_presence_indicators'].append("Has corporate suffix")

            # Check name length appropriateness
            indicators['name_length_appropriate'] = 2 <= len(name_words) <= 5 and 5 <= len(company_name) <= 50
            if indicators['name_length_appropriate']:
                indicators['professional_presence_indicators'].append("Appropriate name length")

            # Check for suspicious keywords
            suspicious_keywords = ['easy', 'fast', 'quick', 'instant', 'guaranteed', 'unlimited', 'free',
                                   'home business', 'work from home', 'make money', 'get rich']
            found_suspicious = [keyword for keyword in suspicious_keywords if keyword in name_lower]
            indicators['contains_suspicious_keywords'] = bool(found_suspicious)
            if found_suspicious:
                indicators['suspicious_indicators'].extend(
                    [f"Suspicious keyword: {keyword}" for keyword in found_suspicious])

            # Check professional naming conventions
            indicators['professional_naming'] = not any(char in company_name for char in '!@#$%^&*()[]{}|;:,.<>?')
            if indicators['professional_naming']:
                indicators['professional_presence_indicators'].append("Professional naming convention")

            # Estimate likelihood of online presence based on name quality
            legitimacy_score = (
                    indicators['has_corporate_suffix'] * 30 +
                    indicators['name_length_appropriate'] * 25 +
                    (not indicators['contains_suspicious_keywords']) * 30 +
                    indicators['professional_naming'] * 15
            )

            # Estimate platform presence
            if legitimacy_score >= 70:
                indicators['has_linkedin_likelihood'] = True
                indicators['has_glassdoor_likelihood'] = True
                indicators['has_official_website_likelihood'] = True
                indicators['professional_presence_indicators'].append("High likelihood of professional online presence")
            elif legitimacy_score >= 50:
                indicators['has_linkedin_likelihood'] = True
                indicators['has_official_website_likelihood'] = True
                indicators['professional_presence_indicators'].append("Moderate likelihood of online presence")
            elif legitimacy_score >= 30:
                indicators['has_linkedin_likelihood'] = False
                indicators['has_official_website_likelihood'] = False
                indicators['suspicious_indicators'].append("Low likelihood of legitimate online presence")
            else:
                indicators['suspicious_indicators'].append("Very low likelihood of legitimate presence")

        return indicators

    def _estimate_search_results(self, company_name: str) -> int:
        """Estimate number of search results based on company name characteristics"""

        if not company_name:
            return 0

        # Base estimation factors
        name_words = len(company_name.split())
        name_length = len(company_name)

        # Estimate based on name characteristics
        if name_length > 30 or name_words > 4:
            return max(10, 50 - (name_length - 30) * 2)  # Very long names get fewer results
        elif name_length < 5:
            return max(5, 20)  # Very short names might be too generic
        else:
            # Normal range estimation
            base_estimate = min(100 + (name_words * 20), 500)

            # Adjust for corporate indicators
            name_lower = company_name.lower()
            if any(suffix in name_lower for suffix in ['inc', 'corp', 'llc', 'ltd', 'company']):
                base_estimate *= 1.5

            # Adjust for suspicious indicators
            if any(suspicious in name_lower for suspicious in ['home business', 'easy money', 'work from home']):
                base_estimate *= 0.3

            return int(min(base_estimate, 1000))

    async def _check_business_patterns(self, company_name: str) -> Dict[str, Any]:
        """Check for common business patterns and red flags"""
        patterns = {
            'appears_generic': False,
            'too_good_to_be_true': False,
            'common_scam_patterns': [],
            'legitimacy_indicators': [],
            'business_type_likelihood': 'unknown',
            'industry_classification': []
        }

        if company_name:
            name_lower = company_name.lower()

            # Check for generic business names
            generic_patterns = ['consulting', 'services', 'solutions', 'group', 'company', 'business', 'enterprise',
                                'corporation', 'international']
            generic_count = sum(1 for pattern in generic_patterns if pattern in name_lower)
            patterns['appears_generic'] = generic_count >= 2

            # Check for scam patterns
            scam_patterns = [
                'home business solutions', 'easy money group', 'financial freedom',
                'work from home company', 'be your own boss', 'unlimited income',
                'quick cash', 'instant profit', 'guaranteed success'
            ]
            found_scam_patterns = [pattern for pattern in scam_patterns if pattern in name_lower]
            patterns['common_scam_patterns'] = found_scam_patterns
            patterns['too_good_to_be_true'] = bool(found_scam_patterns)

            # Check for legitimacy indicators
            legitimacy_indicators = [
                'technologies', 'systems', 'engineering', 'medical', 'healthcare',
                'education', 'research', 'development', 'manufacturing', 'finance',
                'law', 'legal', 'accounting', 'architecture', 'design'
            ]
            found_legitimacy = [indicator for indicator in legitimacy_indicators if indicator in name_lower]
            patterns['legitimacy_indicators'] = found_legitimacy

            # Classify likely business type
            if any(tech in name_lower for tech in ['tech', 'software', 'systems', 'digital', 'cyber']):
                patterns['business_type_likelihood'] = 'technology'
                patterns['industry_classification'].append('Technology')
            elif any(medical in name_lower for medical in ['health', 'medical', 'pharma', 'bio']):
                patterns['business_type_likelihood'] = 'healthcare'
                patterns['industry_classification'].append('Healthcare')
            elif any(finance in name_lower for finance in ['financial', 'bank', 'investment', 'capital']):
                patterns['business_type_likelihood'] = 'financial'
                patterns['industry_classification'].append('Financial Services')
            elif any(service in name_lower for service in ['consulting', 'advisory', 'services']):
                patterns['business_type_likelihood'] = 'services'
                patterns['industry_classification'].append('Professional Services')
            elif patterns['common_scam_patterns']:
                patterns['business_type_likelihood'] = 'suspicious'
                patterns['industry_classification'].append('Potentially Fraudulent')

        return patterns

    async def _analyze_company_name_quality(self, company_name: str) -> Dict[str, Any]:
        """Analyze the quality and professionalism of company name"""
        quality_analysis = {
            'professional_score': 0.0,
            'completeness_score': 0.0,
            'uniqueness_score': 0.0,
            'memorability_score': 0.0,
            'overall_quality': 0.0,
            'quality_factors': [],
            'quality_issues': []
        }

        if company_name:
            name_words = company_name.split()
            name_length = len(company_name)

            # Professional score
            professional_factors = [
                name_length >= 3,  # Not too short
                name_length <= 50,  # Not too long
                not company_name.isupper(),  # Not all caps
                not company_name.islower(),  # Not all lowercase
                len(name_words) >= 2,  # Multiple words
                not any(char.isdigit() for char in company_name[:3]),  # Doesn't start with numbers
                not any(char in company_name for char in '!@#$%^&*()')  # No special characters
            ]
            quality_analysis['professional_score'] = sum(professional_factors) / len(professional_factors) * 100

            if quality_analysis['professional_score'] >= 80:
                quality_analysis['quality_factors'].append("Professional naming convention")
            elif quality_analysis['professional_score'] < 50:
                quality_analysis['quality_issues'].append("Unprofessional naming style")

            # Completeness score
            completeness_factors = [
                bool(company_name.strip()),  # Not empty
                len(name_words) >= 2,  # Multiple words
                any(suffix in company_name.lower() for suffix in
                    ['inc', 'corp', 'llc', 'ltd', 'co', 'company', 'group'])  # Has business suffix
            ]
            quality_analysis['completeness_score'] = sum(completeness_factors) / len(completeness_factors) * 100

            if quality_analysis['completeness_score'] >= 70:
                quality_analysis['quality_factors'].append("Complete business name with proper suffix")
            elif quality_analysis['completeness_score'] < 40:
                quality_analysis['quality_issues'].append("Incomplete or informal business name")

            # Uniqueness score (avoid overly common words)
            common_business_words = ['company', 'business', 'group', 'services', 'solutions', 'consulting',
                                     'international', 'global', 'enterprise']
            unique_words = [word for word in name_words if word.lower() not in common_business_words]
            if len(name_words) > 0:
                quality_analysis['uniqueness_score'] = min(len(unique_words) / len(name_words) * 100, 100)

            if quality_analysis['uniqueness_score'] >= 60:
                quality_analysis['quality_factors'].append("Distinctive and memorable name")
            elif quality_analysis['uniqueness_score'] < 30:
                quality_analysis['quality_issues'].append("Very generic business name")

            # Memorability score (balance of length and complexity)
            if 2 <= len(name_words) <= 3 and 8 <= name_length <= 25:
                quality_analysis['memorability_score'] = 85
                quality_analysis['quality_factors'].append("Good length for memorability")
            elif 1 <= len(name_words) <= 4 and 5 <= name_length <= 35:
                quality_analysis['memorability_score'] = 65
            else:
                quality_analysis['memorability_score'] = 40
                quality_analysis['quality_issues'].append("Name may be difficult to remember")

            # Overall quality (weighted average)
            quality_analysis['overall_quality'] = (
                    quality_analysis['professional_score'] * 0.35 +
                    quality_analysis['completeness_score'] * 0.25 +
                    quality_analysis['uniqueness_score'] * 0.25 +
                    quality_analysis['memorability_score'] * 0.15
            )

        return quality_analysis

    def _calculate_legitimacy_score(self, verification_details: Dict[str, Any]) -> float:
        """Calculate overall company legitimacy score"""
        score = 0.0
        max_score = 100.0

        # Domain analysis (35% weight)
        domain_analysis = verification_details.get('domain_analysis', {})
        if not domain_analysis.get('error'):
            if domain_analysis.get('is_registered', False):
                score += 15

            age_days = domain_analysis.get('age_days', 0)
            if age_days > 1095:  # 3+ years
                score += 15
            elif age_days > 365:  # 1+ years
                score += 10
            elif age_days > 90:  # 3+ months
                score += 5

            if not domain_analysis.get('is_suspicious', True):
                score += 5

        # Domain reputation (10% weight)
        domain_reputation = verification_details.get('domain_reputation', {})
        if not domain_reputation.get('error'):
            reputation_score = domain_reputation.get('reputation_score', 50)
            score += (reputation_score / 100) * 10

        # Online presence (25% weight)
        online_presence = verification_details.get('online_presence', {})
        if not online_presence.get('error'):
            presence_score = online_presence.get('social_media_presence_score', 0)
            score += (presence_score / 100) * 15

            if online_presence.get('search_results_estimated', 0) > 100:
                score += 5
            if online_presence.get('search_results_estimated', 0) > 500:
                score += 5

        # Business patterns (15% weight)
        business_patterns = verification_details.get('business_patterns', {})
        if not business_patterns.get('error'):
            if not business_patterns.get('appears_generic', True):
                score += 5
            if not business_patterns.get('common_scam_patterns', []):
                score += 5
            if business_patterns.get('legitimacy_indicators', []):
                score += min(len(business_patterns['legitimacy_indicators']) * 2, 5)

        # Name quality (15% weight)
        name_quality = verification_details.get('name_quality', {})
        if not name_quality.get('error'):
            quality_score = name_quality.get('overall_quality', 0)
            score += (quality_score / 100) * 15

        return min(score, max_score)

    def _analyze_flags(self, verification_details: Dict[str, Any]) -> tuple:
        """Analyze verification results for red and green flags"""
        red_flags = []
        green_flags = []

        # Domain analysis flags
        domain_analysis = verification_details.get('domain_analysis', {})
        if not domain_analysis.get('error'):
            if domain_analysis.get('is_suspicious', False):
                red_flags.append("Domain is very new (less than 30 days old)")

            age_days = domain_analysis.get('age_days', 0)
            if age_days > 1095:  # 3+ years
                green_flags.append("Domain is well-established (3+ years old)")
            elif age_days > 365:  # 1+ years
                green_flags.append("Domain has reasonable age (1+ years)")

            if domain_analysis.get('registrar'):
                green_flags.append(f"Domain registered with {domain_analysis['registrar']}")

        # Domain reputation flags
        domain_reputation = verification_details.get('domain_reputation', {})
        if not domain_reputation.get('error'):
            if domain_reputation.get('ssl_certificate', False):
                green_flags.append("Website uses SSL certificate")
            else:
                red_flags.append("Website does not use SSL certificate")

            if domain_reputation.get('suspicious_redirects', False):
                red_flags.append("Website has suspicious redirect chains")

        # Business pattern flags
        business_patterns = verification_details.get('business_patterns', {})
        if not business_patterns.get('error'):
            scam_patterns = business_patterns.get('common_scam_patterns', [])
            if scam_patterns:
                red_flags.append(f"Contains scam-related keywords: {', '.join(scam_patterns[:3])}")

            legitimacy_indicators = business_patterns.get('legitimacy_indicators', [])
            if legitimacy_indicators:
                green_flags.append(f"Contains professional keywords: {', '.join(legitimacy_indicators[:3])}")

            if business_patterns.get('business_type_likelihood') == 'suspicious':
                red_flags.append("Business name suggests potentially fraudulent activity")

        # Name quality flags
        name_quality = verification_details.get('name_quality', {})
        if not name_quality.get('error'):
            quality_score = name_quality.get('overall_quality', 0)
            if quality_score < 30:
                red_flags.append("Company name appears unprofessional or incomplete")
            elif quality_score > 70:
                green_flags.append("Company name appears professional and complete")

            quality_issues = name_quality.get('quality_issues', [])
            if quality_issues:
                red_flags.extend(quality_issues[:2])  # Add top 2 quality issues

        # Online presence flags
        online_presence = verification_details.get('online_presence', {})
        if not online_presence.get('error'):
            if online_presence.get('has_linkedin_likelihood', False):
                green_flags.append("Likely has professional LinkedIn presence")

            suspicious_indicators = online_presence.get('suspicious_indicators', [])
            if suspicious_indicators:
                red_flags.extend(suspicious_indicators[:2])  # Add top 2 suspicious indicators

        return red_flags, green_flags

    async def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result when no domain is provided"""
        return {
            'domain': None,
            'is_registered': False,
            'age_days': 0,
            'registrar': None,
            'creation_date': None,
            'expiration_date': None,
            'is_suspicious': False,
            'note': 'No domain provided for analysis'
        }
