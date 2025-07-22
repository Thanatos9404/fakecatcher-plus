import { motion } from 'framer-motion';
import {
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  ChartBarIcon,
  LightBulbIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { GlowingCard } from '../ui/glowing-card';
import type { JobAnalysisResult } from '../../types/api';

interface JobResultsProps {
  results: JobAnalysisResult;
  analysisMode: 'upload' | 'url';
}

const JobResults = ({ results, analysisMode }: JobResultsProps) => {
  const getTrustScoreColor = (score: number) => {
    if (score >= 80) return { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30' };
    if (score >= 60) return { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30' };
    if (score >= 40) return { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/30' };
    return { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/30' };
  };

  const getRiskIcon = (score: number) => {
    if (score >= 80) return CheckCircleIcon;
    if (score >= 60) return InformationCircleIcon;
    if (score >= 40) return ExclamationTriangleIcon;
    return XCircleIcon;
  };

  const trustScore = results.trust_score?.overall_trust_score || 0;
  const colors = getTrustScoreColor(trustScore);
  const RiskIcon = getRiskIcon(trustScore);

  return (
    <motion.div
      initial={{ opacity: 0, y: 100 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -100 }}
      transition={{ duration: 0.8, type: "spring" }}
      className="space-y-8"
    >
      {/* Header */}
      <div className="border-t border-white/10 pt-12">
        <div className="flex items-center justify-center space-x-4 mb-8">
          <motion.h2
            className="text-4xl font-bold text-center bg-gradient-to-r from-white to-blue-300 bg-clip-text text-transparent"
          >
            🔍 Job Posting Analysis Results
          </motion.h2>
          <div className="bg-purple-500/20 px-3 py-1 rounded-full border border-purple-400/30">
            <span className="text-xs text-purple-200">
              {analysisMode === 'upload' ? 'File Analysis' : 'URL Analysis'}
            </span>
          </div>
        </div>

        {/* Trust Score Card */}
        <motion.div className="mb-12">
          <GlowingCard className="p-8 text-center" glowColor="purple">
            <div className="flex items-center justify-center space-x-4 mb-6">
              <h3 className="text-2xl font-bold text-white">Job Posting Trust Score</h3>
            </div>

            <div className="relative inline-block mb-8">
              <motion.div
                className={`w-32 h-32 rounded-full ${colors.bg} border-2 ${colors.border} flex items-center justify-center shadow-2xl`}
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <span className={`text-4xl font-bold ${colors.text}`}>
                  {trustScore}%
                </span>
              </motion.div>
              <div className="absolute -inset-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full blur-xl opacity-50 animate-pulse"></div>
            </div>

            <p className={`text-2xl font-semibold mb-4 ${colors.text}`}>
              {results.trust_score?.trust_level || 'Analysis Complete'}
            </p>
            <p className="text-blue-300">
              {results.trust_score?.risk_assessment || 'Risk assessment completed'}
            </p>
          </GlowingCard>
        </motion.div>

        {/* Analysis Grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          {/* Job Content Analysis */}
          <GlowingCard className="p-6 h-full" glowColor="blue">
            <div className="flex items-center mb-4">
              <ShieldCheckIcon className="w-8 h-8 text-blue-400 mr-3" />
              <h4 className="text-xl font-bold text-white">Job Content Analysis</h4>
            </div>

            <div className="space-y-4">
              {results.job_content?.job_title && (
                <div className="p-3 bg-white/5 rounded-lg">
                  <span className="text-blue-200 text-sm">Job Title:</span>
                  <p className="text-white font-medium">{results.job_content.job_title}</p>
                </div>
              )}

              {results.job_content?.company_name && (
                <div className="p-3 bg-white/5 rounded-lg">
                  <span className="text-blue-200 text-sm">Company:</span>
                  <p className="text-white font-medium">{results.job_content.company_name}</p>
                </div>
              )}

              {results.job_content?.location && (
                <div className="p-3 bg-white/5 rounded-lg">
                  <span className="text-blue-200 text-sm">Location:</span>
                  <p className="text-white font-medium">{results.job_content.location}</p>
                </div>
              )}

              {results.job_content?.red_flag_keywords && results.job_content.red_flag_keywords.length > 0 && (
                <div className="p-3 bg-red-500/10 rounded-lg border border-red-400/20">
                  <span className="text-red-300 text-sm">⚠️ Red Flags Detected:</span>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {results.job_content.red_flag_keywords.slice(0, 3).map((flag, index) => (
                      <span key={index} className="text-xs bg-red-500/20 text-red-200 px-2 py-1 rounded">
                        {flag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </GlowingCard>

          {/* Company Verification */}
          <GlowingCard className="p-6 h-full" glowColor="green">
            <div className="flex items-center mb-4">
              <BuildingOfficeIcon className="w-8 h-8 text-green-400 mr-3" />
              <h4 className="text-xl font-bold text-white">Company Verification</h4>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-green-200">Legitimacy Score:</span>
                <span className="text-white font-semibold">
                  {results.company_verification?.overall_legitimacy_score || 0}%
                </span>
              </div>

              <div className="space-y-2">
                {results.company_verification?.green_flags && results.company_verification.green_flags.length > 0 && (
                  <div>
                    <span className="text-green-300 text-sm">✅ Green Flags:</span>
                    <div className="mt-1">
                      {results.company_verification.green_flags.slice(0, 2).map((flag, index) => (
                        <p key={index} className="text-xs text-green-200 opacity-75">• {flag}</p>
                      ))}
                    </div>
                  </div>
                )}

                {results.company_verification?.red_flags && results.company_verification.red_flags.length > 0 && (
                  <div>
                    <span className="text-red-300 text-sm">❌ Red Flags:</span>
                    <div className="mt-1">
                      {results.company_verification.red_flags.slice(0, 2).map((flag, index) => (
                        <p key={index} className="text-xs text-red-200 opacity-75">• {flag}</p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </GlowingCard>
        </div>

        {/* Web Intelligence */}
        <GlowingCard className="p-6 mb-8" glowColor="purple">
          <div className="flex items-center mb-4">
            <GlobeAltIcon className="w-8 h-8 text-purple-400 mr-3" />
            <h4 className="text-xl font-bold text-white">Web Intelligence</h4>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-white/5 rounded-lg">
              <span className="text-purple-200 text-sm block mb-1">Web Credibility</span>
              <span className="text-2xl font-bold text-white">
                {results.web_intelligence?.overall_web_credibility || 0}%
              </span>
            </div>

            <div className="text-center p-4 bg-white/5 rounded-lg">
              <span className="text-purple-200 text-sm block mb-1">Credibility Factors</span>
              <span className="text-2xl font-bold text-white">
                {results.web_intelligence?.credibility_factors?.length || 0}
              </span>
            </div>

            <div className="text-center p-4 bg-white/5 rounded-lg">
              <span className="text-purple-200 text-sm block mb-1">Warning Signs</span>
              <span className="text-2xl font-bold text-white">
                {results.web_intelligence?.warning_signs?.length || 0}
              </span>
            </div>
          </div>
        </GlowingCard>

        {/* Recommendations */}
        {results.trust_score?.recommendations && (
          <GlowingCard className="p-6 mb-8" glowColor="yellow">
            <div className="flex items-center mb-4">
              <LightBulbIcon className="w-8 h-8 text-yellow-400 mr-3" />
              <h4 className="text-xl font-bold text-white">Recommendations</h4>
            </div>

            <ul className="space-y-3">
              {results.trust_score.recommendations.map((rec, index) => (
                <motion.li
                  key={index}
                  className="flex items-start space-x-3 p-4 bg-white/5 rounded-lg"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <RiskIcon className="w-5 h-5 text-yellow-400 mt-1 flex-shrink-0" />
                  <span className="text-blue-100">{rec}</span>
                </motion.li>
              ))}
            </ul>
          </GlowingCard>
        )}

        {/* Next Steps */}
        {results.trust_score?.next_steps && (
          <GlowingCard className="p-6 mb-8" glowColor="orange">
            <div className="flex items-center mb-4">
              <ChartBarIcon className="w-8 h-8 text-orange-400 mr-3" />
              <h4 className="text-xl font-bold text-white">Next Steps</h4>
            </div>

            <ul className="space-y-3">
              {results.trust_score.next_steps.map((step, index) => (
                <motion.li
                  key={index}
                  className="flex items-start space-x-3 p-4 bg-white/5 rounded-lg"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <span className="text-orange-400 font-bold mt-1 text-sm bg-orange-500/20 w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0">
                    {index + 1}
                  </span>
                  <span className="text-blue-100">{step}</span>
                </motion.li>
              ))}
            </ul>
          </GlowingCard>
        )}

        {/* Processing Details */}
        <motion.div
          className="mt-8 p-4 bg-gray-800/50 rounded-lg border border-gray-600/30"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <details className="text-sm text-gray-300">
            <summary className="cursor-pointer font-medium text-gray-200 hover:text-white flex items-center space-x-2">
              <ClockIcon className="w-4 h-4" />
              <span>Technical Details & Processing Information</span>
            </summary>
            <div className="mt-3 space-y-2 text-xs">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="font-medium text-gray-200 mb-2">Analysis Status:</p>
                  <p>Status: {results.status}</p>
                  <p>Analysis ID: {results.analysis_id}</p>
                  <p>Input Method: {results.input_method}</p>
                  <p>Processing Time: {results.processing_time_seconds?.toFixed(2)}s</p>
                </div>
                <div>
                  <p className="font-medium text-gray-200 mb-2">Component Status:</p>
                  <p>Content Extraction: {results.processing_details?.content_extraction_successful ? '✅' : '❌'}</p>
                  <p>AI Analysis: {results.processing_details?.ai_analysis_successful ? '✅' : '❌'}</p>
                  <p>Company Verification: {results.processing_details?.company_verification_successful ? '✅' : '❌'}</p>
                  <p>Web Intelligence: {results.processing_details?.web_intelligence_successful ? '✅' : '❌'}</p>
                </div>
              </div>

              {results.file_info && (
                <div className="mt-3 pt-3 border-t border-gray-600">
                  <p className="font-medium text-gray-200">File Information:</p>
                  <p>Filename: {results.file_info.filename}</p>
                  <p>File Type: {results.file_info.file_type}</p>
                  <p>Size: {(results.file_info.size_bytes / 1024).toFixed(1)} KB</p>
                </div>
              )}

              {results.url_info && (
                <div className="mt-3 pt-3 border-t border-gray-600">
                  <p className="font-medium text-gray-200">URL Information:</p>
                  <p>Domain: {results.url_info.domain}</p>
                  <p>Secure: {results.url_info.is_secure ? '🔒 HTTPS' : '⚠️ HTTP'}</p>
                </div>
              )}
            </div>
          </details>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default JobResults;
