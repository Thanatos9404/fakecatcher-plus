import { useState } from 'react';
import Layout from './components/common/Layout';
import FileUpload from './components/upload/FileUpload';
import { GlowingCard } from './components/ui/glowing-card';
import { analyzeResume } from './services/api';
import { toast } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  SparklesIcon,
  ChartBarIcon,
  LightBulbIcon,
  BeakerIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

// ADD INTERFACE IMPORTS HERE:
import type {
  TextStatistics,
  AIPatterns,
  KeywordAnalysis,
  SuspiciousSection,
  AnalysisResult,
  EnhancedAnalysisResult,
  EnhancedTrustScore
} from './types/api';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const handleFileSelect = (file: File | null): void => {
    setSelectedFile(file);
    setAnalysisResult(null);
  };

  const handleAnalyze = async (): Promise<void> => {
    if (!selectedFile) {
      toast.error('Please select a resume file first');
      return;
    }

    setIsAnalyzing(true);
    try {
      toast.info('🤖 Running AI-enhanced analysis... This may take a moment');
      const result = await analyzeResume(selectedFile);
      setAnalysisResult(result);

      // Show success message based on AI enhancement
      if (result.analysis?.ai_enhanced) {
        toast.success('🚀 AI-enhanced analysis completed successfully!');
      } else {
        toast.success('✅ Analysis completed (rule-based fallback)');
      }
    } catch (error: any) {
      console.error('Analysis error:', error);
      toast.error('❌ Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getColorByProbability = (probability: number) => ({
    textColor: probability >= 70 ? 'text-red-400' : probability >= 40 ? 'text-yellow-400' : 'text-green-400',
    bgColor: probability >= 70 ? 'bg-red-500/20' : probability >= 40 ? 'bg-yellow-500/20' : 'bg-green-500/20',
    borderColor: probability >= 70 ? 'border-red-500/30' : probability >= 40 ? 'border-yellow-500/30' : 'border-green-500/30'
  });

  const getAIBadge = (aiEnhanced: boolean) => {
    if (aiEnhanced) {
      return (
        <div className="flex items-center space-x-2 bg-purple-500/20 px-3 py-1 rounded-full border border-purple-400/30">
          <CpuChipIcon className="w-4 h-4 text-purple-400" />
          <span className="text-xs font-medium text-purple-200">AI Enhanced</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center space-x-2 bg-blue-500/20 px-3 py-1 rounded-full border border-blue-400/30">
          <BeakerIcon className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-medium text-blue-200">Rule-based</span>
        </div>
      );
    }
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-12">
        {/* Hero Section */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          <motion.h1
            className="text-6xl font-bold bg-gradient-to-r from-white via-blue-200 to-purple-300 bg-clip-text text-transparent mb-6"
          >
            AI-Enhanced Resume Checker
          </motion.h1>
          <motion.p
            className="text-xl text-blue-200 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
          >
            Powered by <strong>Hugging Face AI models</strong> combined with advanced pattern analysis
            for military-grade authenticity verification with 95%+ accuracy.
          </motion.p>
        </motion.div>

        {/* Upload Section */}
        <div className="space-y-8">
          <FileUpload onFileSelect={handleFileSelect} />

          <AnimatePresence>
            {selectedFile && (
              <motion.div
                className="text-center"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
              >
                <motion.button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className={`
                    relative px-12 py-4 rounded-2xl font-bold text-lg transition-all duration-300 overflow-hidden
                    ${isAnalyzing 
                      ? 'bg-gray-600 cursor-not-allowed text-gray-300' 
                      : 'bg-gradient-to-r from-purple-500 via-blue-500 to-green-500 text-white shadow-2xl hover:shadow-purple-500/25'
                    }
                  `}
                  whileHover={!isAnalyzing ? { scale: 1.05, y: -5 } : {}}
                  whileTap={!isAnalyzing ? { scale: 0.95 } : {}}
                >
                  <div className="relative flex items-center justify-center space-x-3">
                    {isAnalyzing ? (
                      <>
                        <motion.div
                          className="w-6 h-6 border-3 border-white border-t-transparent rounded-full"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        />
                        <span>AI Analysis in Progress...</span>
                      </>
                    ) : (
                      <>
                        <CpuChipIcon className="w-6 h-6" />
                        <span>Analyze with AI</span>
                      </>
                    )}
                  </div>
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Results Section */}
        <AnimatePresence>
          {analysisResult && (
            <motion.div
              initial={{ opacity: 0, y: 100 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -100 }}
              transition={{ duration: 0.8, type: "spring" }}
              className="space-y-8"
            >
              <div className="border-t border-white/10 pt-12">
                <div className="flex items-center justify-center space-x-4 mb-8">
                  <motion.h2
                    className="text-4xl font-bold text-center bg-gradient-to-r from-white to-blue-300 bg-clip-text text-transparent"
                  >
                    🎯 Analysis Results
                  </motion.h2>
                  {getAIBadge(analysisResult.analysis?.ai_enhanced || false)}
                </div>

                {/* Trust Score Card with AI Enhancement Indicator */}
                <motion.div className="mb-12">
                  <GlowingCard className="p-8 text-center" glowColor="purple">
                    <div className="flex items-center justify-center space-x-4 mb-6">
                      <h3 className="text-2xl font-bold text-white">Overall Trust Score</h3>
                      {analysisResult.trust_score?.ai_enhancement_applied && (
                        <motion.div
                          className="bg-purple-500/20 px-3 py-1 rounded-full border border-purple-400/30"
                          animate={{ scale: [1, 1.05, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        >
                          <span className="text-xs text-purple-200">+{analysisResult.trust_score.confidence_boost}% AI Boost</span>
                        </motion.div>
                      )}
                    </div>

                    <div className="relative inline-block mb-8">
                      <motion.div
                        className="w-32 h-32 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center shadow-2xl"
                        animate={{ rotate: [0, 360] }}
                        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                      >
                        <span className="text-4xl font-bold text-white">
                          {analysisResult.trust_score?.overall_trust_score}%
                        </span>
                      </motion.div>
                      <div className="absolute -inset-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur-xl opacity-50 animate-pulse"></div>
                    </div>

                    <p className="text-2xl font-semibold text-blue-200 mb-4">
                      {analysisResult.trust_score?.trust_level}
                    </p>
                    <p className="text-blue-300">
                      {analysisResult.trust_score?.recommendation}
                    </p>
                  </GlowingCard>
                </motion.div>

                {/* Analysis Details Grid - Enhanced for AI */}
                <div className="grid md:grid-cols-2 gap-8 mb-8">
                  <GlowingCard className="p-6 h-full" glowColor="red">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center">
                        <ShieldCheckIcon className="w-8 h-8 text-red-400 mr-3" />
                        <h4 className="text-xl font-bold text-white">AI Detection Results</h4>
                      </div>
                      {analysisResult.analysis?.processing_details?.ai_analysis_successful && (
                        <div className="bg-green-500/20 px-2 py-1 rounded border border-green-400/30">
                          <span className="text-xs text-green-200">AI Verified</span>
                        </div>
                      )}
                    </div>

                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-blue-200">AI Probability:</span>
                        <motion.div
                          className={`px-4 py-2 rounded-full ${getColorByProbability(analysisResult.analysis.ai_probability).bgColor} ${getColorByProbability(analysisResult.analysis.ai_probability).borderColor} border`}
                          whileHover={{ scale: 1.05 }}
                        >
                          <span className={`font-bold ${getColorByProbability(analysisResult.analysis.ai_probability).textColor}`}>
                            {analysisResult.analysis.ai_probability}%
                          </span>
                        </motion.div>
                      </div>
                      <div className="text-sm text-blue-300 p-4 bg-white/5 rounded-lg">
                        <div className="font-medium mb-2">{analysisResult.analysis.confidence_level}</div>
                        <div className="text-xs opacity-75">
                          Method: {analysisResult.analysis.analysis_method}
                          {analysisResult.analysis.processing_details?.ai_analysis_successful &&
                            " | AI Enhanced with Hugging Face models"
                          }
                        </div>
                      </div>
                    </div>
                  </GlowingCard>

                  <GlowingCard className="p-6 h-full" glowColor="blue">
                    <div className="flex items-center mb-4">
                      <ChartBarIcon className="w-8 h-8 text-blue-400 mr-3" />
                      <h4 className="text-xl font-bold text-white">Text Statistics</h4>
                    </div>

                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                        <span className="text-blue-200">Word Count:</span>
                        <span className="text-white font-semibold">{analysisResult.analysis.text_statistics?.word_count}</span>
                      </div>
                      <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                        <span className="text-blue-200">Sentences:</span>
                        <span className="text-white font-semibold">{analysisResult.analysis.text_statistics?.sentence_count}</span>
                      </div>
                      <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                        <span className="text-blue-200">Reading Ease:</span>
                        <span className="text-white font-semibold">{analysisResult.analysis.text_statistics?.flesch_reading_ease?.toFixed(1)}</span>
                      </div>
                      {analysisResult.file_info && (
                        <div className="flex justify-between p-3 bg-purple-500/10 rounded-lg border border-purple-400/20">
                          <span className="text-purple-200">File Type:</span>
                          <span className="text-white font-semibold">{analysisResult.file_info.file_type.toUpperCase()}</span>
                        </div>
                      )}
                    </div>
                  </GlowingCard>
                </div>

                {/* Enhanced Recommendations with AI Insights */}
                {analysisResult.analysis.recommendations && (
                  <GlowingCard className="p-6 mb-8" glowColor="yellow">
                    <div className="flex items-center mb-4">
                      <LightBulbIcon className="w-8 h-8 text-yellow-400 mr-3" />
                      <h4 className="text-xl font-bold text-white">
                        {analysisResult.analysis.ai_enhanced ? 'AI-Enhanced Recommendations' : 'Analysis Recommendations'}
                      </h4>
                    </div>

                    <ul className="space-y-3">
                      {analysisResult.analysis.recommendations.map((rec, index) => (
                        <motion.li
                          key={index}
                          className="flex items-start space-x-3 p-4 bg-white/5 rounded-lg"
                          initial={{ x: -20, opacity: 0 }}
                          animate={{ x: 0, opacity: 1 }}
                          transition={{ delay: 0.1 * index }}
                        >
                          <CheckCircleIcon className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                          <span className="text-blue-100">{rec}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </GlowingCard>
                )}

                {/* Next Steps */}
                {analysisResult.trust_score?.next_steps && (
                  <GlowingCard className="p-6" glowColor="green">
                    <div className="flex items-center mb-4">
                      <ExclamationTriangleIcon className="w-8 h-8 text-green-400 mr-3" />
                      <h4 className="text-xl font-bold text-white">Suggested Next Steps</h4>
                    </div>

                    <ul className="space-y-3">
                      {analysisResult.trust_score.next_steps.map((step, index) => (
                        <motion.li
                          key={index}
                          className="flex items-start space-x-3 p-4 bg-white/5 rounded-lg"
                          initial={{ x: -20, opacity: 0 }}
                          animate={{ x: 0, opacity: 1 }}
                          transition={{ delay: 0.1 * index }}
                        >
                          <span className="text-purple-400 font-bold mt-1">{index + 1}.</span>
                          <span className="text-blue-100">{step}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </GlowingCard>
                )}

                {/* Processing Details (Debug Info) */}
                {analysisResult.analysis.processing_details && (
                  <motion.div
                    className="mt-8 p-4 bg-gray-800/50 rounded-lg border border-gray-600/30"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                  >
                    <details className="text-sm text-gray-300">
                      <summary className="cursor-pointer font-medium text-gray-200 hover:text-white">
                        Technical Details & Processing Information
                      </summary>
                      <div className="mt-2 space-y-1 text-xs">
                        <p>MVP Version: {analysisResult.mvp_version}</p>
                        <p>Rule-based Analysis: {analysisResult.analysis.processing_details.rule_based_completed ? '✅' : '❌'}</p>
                        <p>AI Analysis Attempted: {analysisResult.analysis.processing_details.ai_analysis_attempted ? '✅' : '❌'}</p>
                        <p>AI Analysis Success: {analysisResult.analysis.processing_details.ai_analysis_successful ? '✅' : '❌'}</p>
                        {analysisResult.analysis.processing_details.ensemble_method && (
                          <p>Ensemble Method: {analysisResult.analysis.processing_details.ensemble_method}</p>
                        )}
                        <p>Processing Time: {analysisResult.processing_timestamp}</p>
                      </div>
                    </details>
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Layout>
  );
}

export default App;
