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

export interface ResumeAnalysis {
  ai_probability: number;
  confidence_level: string;
  text_statistics: TextStatistics;
  ai_patterns: AIPatterns;
  keyword_analysis: KeywordAnalysis;
  suspicious_sections: SuspiciousSection[];
  recommendations: string[];
}

export interface TrustScoreComponents {
  resume_authenticity: number;
  video_authenticity: string;
  audio_authenticity: string;
}

export interface TrustScore {
  overall_trust_score: number;
  trust_level: string;
  components: TrustScoreComponents;
  recommendation: string;
  next_steps: string[];
}

export interface AnalysisResult {
  status: string;
  analysis: ResumeAnalysis;
  trust_score: TrustScore;
  mvp_version: string;
}

export interface HealthCheckResponse {
  status: string;
  version: string;
}

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
}
