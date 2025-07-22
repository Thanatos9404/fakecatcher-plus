import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BriefcaseIcon,
  LinkIcon,
  PhotoIcon,
  DocumentIcon,
  SparklesIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import JobUpload from './JobUpload';
import URLInput from './URLInput';
import JobResults from './JobResults';
import { analyzeJobPosting } from '../../services/api';
import { toast } from 'react-toastify';
import type { JobAnalysisResult } from '../../types/api';

type AnalysisMode = 'upload' | 'url';
type FileType = 'image' | 'pdf';

const JobAnalyzer = () => {
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('upload');
  const [fileType, setFileType] = useState<FileType>('image');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<JobAnalysisResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobUrl, setJobUrl] = useState<string>('');

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setAnalysisResult(null);
  };

  const handleUrlChange = (url: string) => {
    setJobUrl(url);
    setAnalysisResult(null);
  };

  const handleAnalyze = async () => {
    if (analysisMode === 'upload' && !selectedFile) {
      toast.error('Please select a file first');
      return;
    }

    if (analysisMode === 'url' && !jobUrl.trim()) {
      toast.error('Please enter a job posting URL');
      return;
    }

    setIsAnalyzing(true);
    try {
      toast.info('🔍 Analyzing job posting... This may take a moment');

      let result: JobAnalysisResult;

      if (analysisMode === 'upload') {
        result = await analyzeJobPosting({ file: selectedFile!, type: fileType });
      } else {
        result = await analyzeJobPosting({ url: jobUrl });
      }

      setAnalysisResult(result);
      toast.success('✅ Job posting analysis completed!');
    } catch (error: any) {
      console.error('Job analysis error:', error);
      toast.error('❌ Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getModeIcon = (mode: AnalysisMode) => {
    return mode === 'upload' ? PhotoIcon : LinkIcon;
  };

  const getFileTypeIcon = (type: FileType) => {
    return type === 'image' ? PhotoIcon : DocumentIcon;
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="flex items-center justify-center space-x-3 mb-4">
          <BriefcaseIcon className="w-12 h-12 text-purple-400" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-blue-300 to-green-300 bg-clip-text text-transparent">
            Job Posting Verification
          </h1>
        </div>
        <p className="text-xl text-blue-200 max-w-3xl mx-auto leading-relaxed">
          Protect yourself from fake job postings and recruitment scams with AI-powered authenticity verification
        </p>
      </motion.div>

      {/* Mode Selection */}
      <motion.div
        className="glass-card p-6"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <h3 className="text-lg font-semibold text-white mb-4">Choose Analysis Method</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {(['upload', 'url'] as AnalysisMode[]).map((mode) => {
            const Icon = getModeIcon(mode);
            const isSelected = analysisMode === mode;

            return (
              <motion.button
                key={mode}
                onClick={() => setAnalysisMode(mode)}
                className={`
                  relative p-6 rounded-xl border transition-all duration-300
                  ${isSelected 
                    ? 'border-purple-400 bg-purple-500/20 text-white' 
                    : 'border-white/20 bg-white/5 text-blue-200 hover:border-purple-400/50 hover:bg-purple-500/10'
                  }
                `}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Icon className={`w-8 h-8 mx-auto mb-3 ${isSelected ? 'text-purple-300' : 'text-blue-300'}`} />
                <h4 className="font-medium mb-2">
                  {mode === 'upload' ? 'Upload File' : 'Analyze URL'}
                </h4>
                <p className="text-sm opacity-75">
                  {mode === 'upload'
                    ? 'Upload image or PDF of job posting'
                    : 'Enter job posting URL for analysis'
                  }
                </p>
                {isSelected && (
                  <motion.div
                    className="absolute inset-0 border-2 border-purple-400 rounded-xl"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  />
                )}
              </motion.button>
            );
          })}
        </div>

        {/* File Type Selection for Upload Mode */}
        {analysisMode === 'upload' && (
          <motion.div
            className="mt-6"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.4 }}
          >
            <h4 className="text-md font-medium text-white mb-3">File Type</h4>
            <div className="flex space-x-4">
              {(['image', 'pdf'] as FileType[]).map((type) => {
                const Icon = getFileTypeIcon(type);
                const isSelected = fileType === type;

                return (
                  <motion.button
                    key={type}
                    onClick={() => setFileType(type)}
                    className={`
                      flex items-center space-x-2 px-4 py-2 rounded-lg border transition-all duration-200
                      ${isSelected 
                        ? 'border-green-400 bg-green-500/20 text-green-200' 
                        : 'border-white/20 bg-white/5 text-blue-200 hover:border-green-400/50'
                      }
                    `}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-medium">
                      {type === 'image' ? 'Image (JPG, PNG)' : 'PDF Document'}
                    </span>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Input Interface */}
      <AnimatePresence mode="wait">
        {analysisMode === 'upload' ? (
          <motion.div
            key="upload"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.5 }}
          >
            <JobUpload
              fileType={fileType}
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
            />
          </motion.div>
        ) : (
          <motion.div
            key="url"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.5 }}
          >
            <URLInput
              url={jobUrl}
              onUrlChange={handleUrlChange}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Analysis Button */}
      <AnimatePresence>
        {((analysisMode === 'upload' && selectedFile) || (analysisMode === 'url' && jobUrl.trim())) && (
          <motion.div
            className="text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.4 }}
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
                    <span>Analyzing Job Posting...</span>
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-6 h-6" />
                    <span>Verify Job Authenticity</span>
                  </>
                )}
              </div>
            </motion.button>

            {!isAnalyzing && (
              <motion.p
                className="text-sm text-blue-300 mt-3"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <ExclamationTriangleIcon className="w-4 h-4 inline mr-1" />
                AI analysis will check for scam patterns, company legitimacy, and web presence
              </motion.p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Analysis Results */}
      <AnimatePresence>
        {analysisResult && (
          <JobResults
            results={analysisResult}
            analysisMode={analysisMode}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default JobAnalyzer;
