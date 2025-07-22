import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  LinkIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

interface URLInputProps {
  url: string;
  onUrlChange: (url: string) => void;
}

const URLInput = ({ url, onUrlChange }: URLInputProps) => {
  const [isValidUrl, setIsValidUrl] = useState(false);
  const [urlError, setUrlError] = useState<string>('');

  const validateUrl = (inputUrl: string) => {
    try {
      const urlPattern = /^https?:\/\/.+/;
      if (!urlPattern.test(inputUrl)) {
        setUrlError('URL must start with http:// or https://');
        setIsValidUrl(false);
        return;
      }

      new URL(inputUrl);
      setIsValidUrl(true);
      setUrlError('');
    } catch {
      setUrlError('Please enter a valid URL');
      setIsValidUrl(false);
    }
  };

  const handleUrlChange = (inputUrl: string) => {
    onUrlChange(inputUrl);
    if (inputUrl.trim()) {
      validateUrl(inputUrl.trim());
    } else {
      setIsValidUrl(false);
      setUrlError('');
    }
  };

  const commonJobSites = [
    { name: 'LinkedIn', domain: 'linkedin.com', color: 'blue' },
    { name: 'Indeed', domain: 'indeed.com', color: 'green' },
    { name: 'Glassdoor', domain: 'glassdoor.com', color: 'purple' },
    { name: 'AngelList', domain: 'angel.co', color: 'orange' },
    { name: 'Monster', domain: 'monster.com', color: 'red' },
  ];

  const handleQuickFill = (domain: string) => {
    const sampleUrl = `https://www.${domain}/jobs/example-posting`;
    handleUrlChange(sampleUrl);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Main URL Input Card */}
      <div className="glass-card p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-green-500 rounded-xl flex items-center justify-center">
            <LinkIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Job Posting URL</h3>
            <p className="text-blue-200 text-sm">Enter the direct link to analyze</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <GlobeAltIcon className="h-5 w-5 text-blue-300" />
            </div>

            <input
              type="url"
              value={url}
              onChange={(e) => handleUrlChange(e.target.value)}
              placeholder="https://example.com/jobs/software-engineer"
              className="
                w-full pl-12 pr-12 py-4
                bg-white/10 backdrop-blur-sm
                border border-white/20 rounded-xl
                text-white placeholder-blue-300
                focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent
                transition-all duration-300
              "
            />

            {url && (
              <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
                {isValidUrl ? (
                  <CheckCircleIcon className="h-5 w-5 text-green-400" />
                ) : urlError ? (
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
                ) : null}
              </div>
            )}
          </div>

          {/* URL Status */}
          {url && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="flex items-center space-x-2"
            >
              {isValidUrl ? (
                <>
                  <CheckCircleIcon className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-green-300">Valid URL format</span>
                </>
              ) : urlError ? (
                <>
                  <ExclamationTriangleIcon className="w-4 h-4 text-red-400" />
                  <span className="text-sm text-red-300">{urlError}</span>
                </>
              ) : null}
            </motion.div>
          )}
        </div>
      </div>

      {/* Common Job Sites Quick Access */}
      <div className="glass-card p-6">
        <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <SparklesIcon className="w-5 h-5 text-purple-400" />
          <span>Popular Job Sites</span>
        </h4>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {commonJobSites.map((site) => (
            <motion.button
              key={site.domain}
              onClick={() => handleQuickFill(site.domain)}
              className="
                p-3 rounded-lg border border-white/20 bg-white/5
                hover:border-purple-400/50 hover:bg-purple-500/10
                transition-all duration-200 text-center
              "
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className={`w-8 h-8 bg-${site.color}-500 rounded-full mx-auto mb-2 flex items-center justify-center`}>
                <GlobeAltIcon className="w-4 h-4 text-white" />
              </div>
              <span className="text-sm font-medium text-white">{site.name}</span>
              <p className="text-xs text-blue-300 mt-1">{site.domain}</p>
            </motion.button>
          ))}
        </div>

        <p className="text-xs text-blue-300 mt-4 text-center opacity-75">
          Click any site above to fill in a sample URL format
        </p>
      </div>

      {/* Analysis Preview */}
      {isValidUrl && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-6"
        >
          <h4 className="text-lg font-semibold text-white mb-3">Analysis Preview</h4>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-blue-200">Domain:</span>
              <span className="text-white font-medium">
                {new URL(url).hostname}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-blue-200">SSL Status:</span>
              <span className={`font-medium ${url.startsWith('https') ? 'text-green-300' : 'text-yellow-300'}`}>
                {url.startsWith('https') ? '🔒 Secure' : '⚠️ Not Secure'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-blue-200">Analysis Type:</span>
              <span className="text-white font-medium">
                Web scraping + AI verification
              </span>
            </div>
          </div>

          <div className="mt-4 p-3 bg-blue-500/10 rounded-lg border border-blue-400/20">
            <p className="text-xs text-blue-200">
              <CheckCircleIcon className="w-4 h-4 inline mr-1" />
              URL will be analyzed for content authenticity, company verification, and scam detection
            </p>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default URLInput;
