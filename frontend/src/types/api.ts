// Basic interfaces for resume analysis
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

// Enhanced analysis result interface (this was missing)
export interface ExtendedAnalysisResult {
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

// Job posting specific interfaces
export interface JobContent {
  job_title?: string;
  company_name?: string;
  salary_range?: {
    found: boolean;
    min_salary?: number;
    max_salary?: number;
    period?: string;
    raw_text?: string;
    is_suspicious: boolean;
  };
  location?: string;
  job_description: string;
  requirements: string[];
  contact_info: {
    email?: string;
    phone?: string;
    website?: string;
  };
  application_method: string;
  posting_date?: string;
  red_flag_keywords: string[];
  extraction_method: string;
  raw_text: string;
  source_url?: string;
  domain?: string;
}

export interface CompanyVerification {
  company_name: string;
  company_domain?: string;
  overall_legitimacy_score: number;
  verification_details: {
    domain_analysis: any;
    online_presence: any;
    business_patterns: any;
    name_quality: any;
    domain_reputation?: any;
  };
  red_flags: string[];
  green_flags: string[];
  analysis_timestamp: string;
}

export interface WebIntelligence {
  company_name: string;
  analysis_timestamp: string;
  domain_analysis: any;
  social_media_presence: any;
  review_analysis: any;
  job_board_presence: any;
  source_url_analysis?: any;
  overall_web_credibility: number;
  credibility_factors: string[];
  warning_signs: string[];
}

export interface JobTrustScore {
  overall_trust_score: number;
  trust_level: string;
  risk_assessment: string;
  component_breakdown: {
    [key: string]: {
      score: number;
      weight: number;
      contribution: number;
    };
  };
  recommendations: string[];
  next_steps: string[];
  analysis_summary: string;
  calculation_timestamp: string;
}

export interface JobAnalysisResult {
  analysis_id: string;
  input_type: string;
  analysis_timestamp: string;
  status: string;
  job_content: JobContent;
  content_analysis: any;
  company_verification: CompanyVerification;
  web_intelligence: WebIntelligence;
  trust_score: JobTrustScore;
  processing_details: {
    content_extraction_successful: boolean;
    ai_analysis_successful: boolean;
    company_verification_successful: boolean;
    web_intelligence_successful: boolean;
    trust_calculation_successful: boolean;
  };
  errors: string[];
  warnings: string[];
  processing_time_seconds?: number;
  file_info?: {
    filename: string;
    size_bytes: number;
    file_type: string;
    content_type: string;
  };
  url_info?: {
    original_url: string;
    validated_url: string;
    domain: string;
    is_secure: boolean;
  };
  analysis_type: string;
  input_method?: string;
}

// AI Analysis interfaces
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

// Main analysis result interfaces
export interface ComprehensiveAnalysisResult {
  status: string;
  analysis: ExtendedAnalysisResult;
  trust_score: EnhancedTrustScore;
  mvp_version: string;
  file_info?: {
    filename: string;
    size_bytes: number;
    text_length: number;
    file_type: string;
  };
  processing_timestamp: string;
  detailed_analysis?: any;
  analysis_type: string;
}

// Health check interface
export interface HealthCheckResponse {
  status: string;
  version?: string;
  api_accessible?: boolean;
  model_ready?: boolean;
  cache_enabled?: boolean;
  api_key_configured?: boolean;
}

// Generic API response wrapper
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: string;
}

// Union type for all analysis results
export type AnalysisResult = ComprehensiveAnalysisResult | JobAnalysisResult;

// Export additional utility types
export type InputType = 'resume' | 'job_posting_file' | 'job_posting_url';
export type AnalysisType = 'resume' | 'job_posting';
export type FileType = 'pdf' | 'doc' | 'docx' | 'image';
