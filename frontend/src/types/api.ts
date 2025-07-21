// Basic interfaces that were missing
export interface TextStatistics {
  flesch_reading_ease: number;
  flesch_kincaid_grade: number;
  automated_readability_index: number;
  sentence_count: number;
  word_count: number;
  avg_sentence_length: number;
  perplexity_score: number;
}

export interface AIPatterns {
  repetitive_structures: number;
  perfect_grammar_score: number;
  buzzword_density: number;
  sentence_uniformity: number;
  transition_overuse: number;
}

export interface KeywordAnalysis {
  ai_buzzwords_found: string[];
  excessive_adjectives: string[];
  buzzword_count: number;
  adjective_ratio: number;
}

export interface SuspiciousSection {
  text: string;
  sentence_number: number;
  reasons: string[];
}

export interface AIAnalysisDetails {
  ai_probability: number;
  confidence_level: string;
  human_probability: number;
  mixed_probability: number;
  analysis_method: string;
  model_used: string;
  detailed_scores: {
    ai_generated: number;
    human_written: number;
    mixed_human_ai: number;
  };
  analysis_details: {
    text_length: number;
    analysis_scope: string;
    detection_category: string;
    risk_assessment: string;
    recommended_actions: string[];
  };
  processing_timestamp: string;
}

export interface EnhancedAnalysisResult {
  ai_probability: number;
  confidence_level: string;
  analysis_method: string;
  ai_enhanced: boolean;
  text_statistics: TextStatistics;
  ai_patterns: AIPatterns;
  keyword_analysis: KeywordAnalysis;
  suspicious_sections: SuspiciousSection[];
  recommendations: string[];
  processing_details: {
    rule_based_completed: boolean;
    ai_analysis_attempted: boolean;
    ai_analysis_successful: boolean;
    ensemble_method?: string;
    ai_weight?: number;
    rule_weight?: number;
  };
}

export interface EnhancedTrustScore {
  overall_trust_score: number;
  trust_level: string;
  ai_enhancement_applied?: boolean;
  confidence_boost?: number;
  components: {
    resume_authenticity: number;
    ai_verification: string;
    video_authenticity: string;
    audio_authenticity: string;
  };
  recommendation: string;
  next_steps: string[];
}

export interface ComprehensiveAnalysisResult {
  status: string;
  analysis: EnhancedAnalysisResult;
  trust_score: EnhancedTrustScore;
  mvp_version: string;
  file_info: {
    filename: string;
    size_bytes: number;
    text_length: number;
    file_type: string;
  };
  processing_timestamp: string;
  detailed_analysis?: any;
}

export interface HealthCheckResponse {
  status: string;
  version: string;
}

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
}

// Main analysis result interface (supports both versions)
export interface AnalysisResult extends ComprehensiveAnalysisResult {}
