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
  LightBulbIcon
} from '@heroicons/react/24/outline';
import type { AnalysisResult } from './types/api';

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
      toast.info('🔍 Analyzing resume with advanced AI...');
      const result = await analyzeResume(selectedFile);
      setAnalysisResult(result);
      toast.success('✅ Analysis completed successfully!');
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
            animate={{
              backgroundPosition: ["0%", "100%"],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              repeatType: "reverse"
            }}
          >
            Resume Authenticity Checker
          </motion.h1>
          <motion.p
            className="text-xl text-blue-200 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
          >
            Upload a resume and let our cutting-edge AI analyze it for potential AI-generated content,
            suspicious patterns, and authenticity indicators with military-grade precision.
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
                      : 'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white shadow-2xl hover:shadow-purple-500/25'
                    }
                  `}
                  whileHover={!isAnalyzing ? { scale: 1.05, y: -5 } : {}}
                  whileTap={!isAnalyzing ? { scale: 0.95 } : {}}
                >
                  {isAnalyzing && (
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600"
                      animate={{ x: ["-100%", "100%"] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  )}

                  <div className="relative flex items-center justify-center space-x-3">
                    {isAnalyzing ? (
                      <>
                        <motion.div
                          className="w-6 h-6 border-3 border-white border-t-transparent rounded-full"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        />
                        <span>Analyzing Resume...</span>
                      </>
                    ) : (
                      <>
                        <SparklesIcon className="w-6 h-6" />
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
                <motion.h2
                  className="text-4xl font-bold text-center bg-gradient-to-r from-white to-blue-300 bg-clip-text text-transparent mb-12"
                  animate={{ scale: [1, 1.02, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  🎯 Analysis Results
                </motion.h2>

                {/* Trust Score Card */}
                <motion.div
                  className="mb-12"
                  whileHover={{ y: -10 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <GlowingCard className="p-8 text-center" glowColor="purple">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.8, delay: 0.2 }}
                    >
                      <h3 className="text-2xl font-bold text-white mb-8">Overall Trust Score</h3>

                      <div className="relative inline-block mb-8">
                        <motion.div
                          className="w-32 h-32 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center shadow-2xl"
                          animate={{ rotate: [0, 360] }}
                          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                        >
                          <motion.span
                            className="text-4xl font-bold text-white"
                            animate={{ scale: [1, 1.1, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                          >
                            {analysisResult.trust_score?.overall_trust_score}%
                          </motion.span>
                        </motion.div>

                        {/* Glow ring */}
                        <div className="absolute -inset-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur-xl opacity-50 animate-pulse"></div>
                      </div>

                      <p className="text-2xl font-semibold text-blue-200 mb-4">
                        {analysisResult.trust_score?.trust_level}
                      </p>
                      <p className="text-blue-300">
                        {analysisResult.trust_score?.recommendation}
                      </p>
                    </motion.div>
                  </GlowingCard>
                </motion.div>

                {/* Analysis Details Grid */}
                <div className="grid md:grid-cols-2 gap-8 mb-8">
                  <motion.div
                    initial={{ x: -100, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                  >
                    <GlowingCard className="p-6 h-full" glowColor="red">
                      <div className="flex items-center mb-4">
                        <ShieldCheckIcon className="w-8 h-8 text-red-400 mr-3" />
                        <h4 className="text-xl font-bold text-white">AI Detection Results</h4>
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
                          {analysisResult.analysis.confidence_level}
                        </div>
                      </div>
                    </GlowingCard>
                  </motion.div>

                  <motion.div
                    initial={{ x: 100, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                  >
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
                      </div>
                    </GlowingCard>
                  </motion.div>
                </div>

                {/* Recommendations */}
                {analysisResult.analysis.recommendations && (
                  <motion.div
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    className="mb-8"
                  >
                    <GlowingCard className="p-6" glowColor="yellow">
                      <div className="flex items-center mb-4">
                        <LightBulbIcon className="w-8 h-8 text-yellow-400 mr-3" />
                        <h4 className="text-xl font-bold text-white">AI Recommendations</h4>
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
                  </motion.div>
                )}

                {/* Next Steps */}
                {analysisResult.trust_score?.next_steps && (
                  <motion.div
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.6 }}
                  >
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
