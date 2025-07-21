import re
import asyncio
from typing import Dict, List, Any
import textstat
import numpy as np
from collections import Counter


class ResumeAnalyzer:
    """Resume AI detection and analysis"""

    def __init__(self):
        self.ai_indicators = [
            "passionate", "driven", "results-oriented", "team player",
            "think outside the box", "synergy", "leverage", "paradigm",
            "holistic approach", "cutting-edge", "state-of-the-art",
            "robust", "scalable", "optimized", "enhanced"
        ]

        self.excessive_adjectives = [
            "exceptional", "outstanding", "remarkable", "extraordinary",
            "phenomenal", "incredible", "amazing", "fantastic"
        ]

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Comprehensive resume analysis"""

        # Basic text statistics
        text_stats = self._calculate_text_statistics(text)

        # AI pattern detection
        ai_patterns = await self._detect_ai_patterns(text)

        # Keyword analysis
        keyword_analysis = self._analyze_keywords(text)

        # Calculate final AI probability
        ai_probability = self._calculate_ai_probability(
            text_stats, ai_patterns, keyword_analysis
        )

        return {
            "ai_probability": round(ai_probability, 2),
            "confidence_level": self._get_confidence_level(ai_probability),
            "text_statistics": text_stats,
            "ai_patterns": ai_patterns,
            "keyword_analysis": keyword_analysis,
            "suspicious_sections": self._identify_suspicious_sections(text),
            "recommendations": self._generate_recommendations(ai_probability)
        }

    def _calculate_text_statistics(self, text: str) -> Dict[str, float]:
        """Calculate text complexity metrics"""
        return {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "automated_readability_index": textstat.automated_readability_index(text),
            "sentence_count": textstat.sentence_count(text),
            "word_count": textstat.lexicon_count(text),
            "avg_sentence_length": textstat.avg_sentence_length(text),
            "perplexity_score": self._calculate_perplexity(text)
        }

    def _calculate_perplexity(self, text: str) -> float:
        """Simple perplexity-like calculation"""
        words = text.lower().split()
        if len(words) < 10:
            return 50.0

        word_freq = Counter(words)
        total_words = len(words)

        # Simple entropy calculation
        entropy = 0
        for word, freq in word_freq.items():
            prob = freq / total_words
            entropy -= prob * np.log2(prob)

        return min(entropy * 10, 100)  # Scale to 0-100

    async def _detect_ai_patterns(self, text: str) -> Dict[str, Any]:
        """Detect AI-generated patterns"""
        text_lower = text.lower()

        # Pattern checks
        patterns = {
            "repetitive_structures": self._check_repetitive_structures(text),
            "perfect_grammar_score": self._assess_grammar_perfection(text),
            "buzzword_density": self._calculate_buzzword_density(text_lower),
            "sentence_uniformity": self._check_sentence_uniformity(text),
            "transition_overuse": self._check_transition_overuse(text_lower)
        }

        return patterns

    def _check_repetitive_structures(self, text: str) -> float:
        """Check for repetitive sentence structures"""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) < 3:
            return 0.0

        # Simple pattern: sentences starting with similar words
        first_words = []
        for sentence in sentences:
            words = sentence.strip().split()
            if words:
                first_words.append(words[0].lower())

        if not first_words:
            return 0.0

        # Calculate repetition rate
        word_counts = Counter(first_words)
        max_repeat = max(word_counts.values())
        repetition_rate = (max_repeat / len(first_words)) * 100

        return min(repetition_rate, 100)

    def _assess_grammar_perfection(self, text: str) -> float:
        """Assess if grammar is suspiciously perfect"""
        # Simple heuristic: check for common human errors
        human_indicators = [
            r'\bi\s',  # lowercase 'i'
            r'\s{2,}',  # multiple spaces
            r'[.]{2,}',  # multiple periods
            r'[!]{2,}',  # multiple exclamations
        ]

        error_count = 0
        for pattern in human_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            error_count += len(matches)

        # Perfect grammar (no human errors) is suspicious
        perfection_score = max(0, 100 - (error_count * 10))
        return min(perfection_score, 100)

    def _calculate_buzzword_density(self, text: str) -> float:
        """Calculate density of AI-favorite buzzwords"""
        words = text.split()
        if not words:
            return 0.0

        buzzword_count = sum(1 for word in words if word in self.ai_indicators)
        density = (buzzword_count / len(words)) * 100

        return min(density, 100)

    def _check_sentence_uniformity(self, text: str) -> float:
        """Check if sentences are suspiciously uniform in length"""
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.strip().split()) for s in sentences if s.strip()]

        if len(sentence_lengths) < 3:
            return 0.0

        # Calculate coefficient of variation
        mean_length = np.mean(sentence_lengths)
        std_length = np.std(sentence_lengths)

        if mean_length == 0:
            return 0.0

        cv = std_length / mean_length
        uniformity_score = max(0, 100 - (cv * 50))  # Lower CV = more uniform = more suspicious

        return min(uniformity_score, 100)

    def _check_transition_overuse(self, text: str) -> float:
        """Check for overuse of AI-favorite transitions"""
        transitions = [
            "furthermore", "moreover", "additionally", "consequently",
            "therefore", "thus", "hence", "accordingly", "nevertheless"
        ]

        transition_count = sum(text.count(transition) for transition in transitions)
        words = text.split()

        if not words:
            return 0.0

        density = (transition_count / len(words)) * 1000  # Per 1000 words
        return min(density, 100)

    def _analyze_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze keyword usage patterns"""
        words = text.lower().split()

        return {
            "ai_buzzwords_found": [word for word in words if word in self.ai_indicators],
            "excessive_adjectives": [word for word in words if word in self.excessive_adjectives],
            "buzzword_count": len([word for word in words if word in self.ai_indicators]),
            "adjective_ratio": len([word for word in words if word in self.excessive_adjectives]) / max(len(words), 1)
        }

    def _calculate_ai_probability(self, stats: Dict, patterns: Dict, keywords: Dict) -> float:
        """Calculate overall AI probability score"""

        # Weight different factors
        factors = {
            "perplexity": min(max((100 - stats["perplexity_score"]) / 100, 0), 1) * 0.15,
            "buzzword_density": patterns["buzzword_density"] / 100 * 0.25,
            "perfect_grammar": patterns["perfect_grammar_score"] / 100 * 0.20,
            "repetitive_structures": patterns["repetitive_structures"] / 100 * 0.15,
            "sentence_uniformity": patterns["sentence_uniformity"] / 100 * 0.15,
            "transition_overuse": patterns["transition_overuse"] / 100 * 0.10
        }

        total_score = sum(factors.values()) * 100
        return min(max(total_score, 0), 100)

    def _get_confidence_level(self, probability: float) -> str:
        """Get confidence level based on probability"""
        if probability >= 80:
            return "High Confidence - Likely AI Generated"
        elif probability >= 60:
            return "Medium-High Confidence - Probably AI Generated"
        elif probability >= 40:
            return "Medium Confidence - Possibly AI Generated"
        elif probability >= 20:
            return "Low-Medium Confidence - Unlikely AI Generated"
        else:
            return "Low Confidence - Likely Human Written"

    def _identify_suspicious_sections(self, text: str) -> List[Dict[str, str]]:
        """Identify specific suspicious sections"""
        suspicious_sections = []
        sentences = re.split(r'[.!?]+', text)

        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            sentence_lower = sentence.lower()
            suspicion_reasons = []

            # Check for buzzword concentration
            buzzword_count = sum(1 for word in self.ai_indicators if word in sentence_lower)
            if buzzword_count >= 2:
                suspicion_reasons.append("High buzzword concentration")

            # Check for excessive adjectives
            adj_count = sum(1 for word in self.excessive_adjectives if word in sentence_lower)
            if adj_count >= 1:
                suspicion_reasons.append("Excessive adjectives")

            if suspicion_reasons:
                suspicious_sections.append({
                    "text": sentence.strip(),
                    "sentence_number": i + 1,
                    "reasons": suspicion_reasons
                })

        return suspicious_sections[:5]  # Return top 5 suspicious sections

    def _generate_recommendations(self, ai_probability: float) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if ai_probability >= 70:
            recommendations.extend([
                "⚠️ High likelihood of AI generation detected",
                "📝 Request clarification on specific experiences mentioned",
                "🤔 Consider conducting detailed technical interviews",
                "📞 Verify accomplishments through references"
            ])
        elif ai_probability >= 40:
            recommendations.extend([
                "⚡ Some AI patterns detected - proceed with caution",
                "✅ Verify key claims during interview process",
                "📋 Ask for specific examples of mentioned projects"
            ])
        else:
            recommendations.append("✅ Resume appears to be human-written")

        return recommendations
