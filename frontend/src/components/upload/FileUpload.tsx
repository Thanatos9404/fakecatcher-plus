import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import type { FileRejection } from 'react-dropzone';
import { CloudArrowUpIcon, DocumentTextIcon, XMarkIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import { GlowingCard } from '../ui/glowing-card';

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
  maxSize?: number;
}

const FileUpload = ({
  onFileSelect,
  maxSize = 10485760
}: FileUploadProps) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    setIsDragOver(false);

    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0];
      alert(`File rejected: ${error.message}`);
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setUploadedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const onDragEnter = useCallback(() => {
    setIsDragOver(true);
  }, []);

  const onDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDragEnter,
    onDragLeave,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize,
    multiple: false
  });

  const removeFile = (): void => {
    setUploadedFile(null);
    onFileSelect(null);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (uploadedFile) {
    return (
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          <GlowingCard className="p-6" glowColor="green">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <motion.div
                  className="w-16 h-16 bg-gradient-to-br from-green-400 to-blue-500 rounded-2xl flex items-center justify-center shadow-xl"
                  animate={{ rotate: [0, 5, -5, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <DocumentTextIcon className="w-8 h-8 text-white" />
                </motion.div>
                <div>
                  <p className="font-semibold text-white text-lg">{uploadedFile.name}</p>
                  <p className="text-blue-200">{formatFileSize(uploadedFile.size)}</p>
                  <div className="flex items-center mt-2 space-x-1">
                    <SparklesIcon className="w-4 h-4 text-yellow-400" />
                    <span className="text-xs text-yellow-300">Ready for AI analysis</span>
                  </div>
                </div>
              </div>
              <motion.button
                onClick={removeFile}
                className="p-3 text-red-400 hover:text-red-300 rounded-full hover:bg-red-500/20 transition-all"
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
              >
                <XMarkIcon className="w-6 h-6" />
              </motion.button>
            </div>
          </GlowingCard>
        </motion.div>
      </AnimatePresence>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
    >
      <div
        {...getRootProps()}
        className={`
          relative cursor-pointer transition-all duration-500 transform
          ${isDragActive || isDragOver 
            ? 'scale-105' 
            : 'hover:scale-102'
          }
        `}
      >
        <input {...getInputProps()} />

        {/* Glow effects */}
        <div className={`absolute -inset-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-3xl blur-xl opacity-30 transition-opacity duration-500 ${
          isDragActive ? 'opacity-70' : 'opacity-30'
        }`}></div>

        {/* Main upload area */}
        <div className="relative glass-card p-12 text-center">
          {/* Floating particles */}
          <div className="absolute inset-0 overflow-hidden rounded-3xl">
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-blue-400 rounded-full"
                animate={{
                  x: [Math.random() * 400, Math.random() * 400],
                  y: [Math.random() * 300, Math.random() * 300],
                }}
                transition={{
                  duration: 10 + Math.random() * 10,
                  repeat: Infinity,
                  repeatType: "reverse"
                }}
                style={{
                  left: Math.random() * 100 + '%',
                  top: Math.random() * 100 + '%',
                }}
              />
            ))}
          </div>

          <motion.div
            animate={{ y: isDragActive ? -10 : 0 }}
            transition={{ type: "spring", stiffness: 400 }}
          >
            <motion.div
              className="relative inline-block"
              animate={{ rotate: isDragActive ? 360 : 0 }}
              transition={{ duration: 1 }}
            >
              <CloudArrowUpIcon className="w-24 h-24 text-blue-300 mx-auto mb-6 filter drop-shadow-xl" />
              {isDragActive && (
                <motion.div
                  className="absolute inset-0 bg-blue-400 rounded-full blur-xl opacity-50"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              )}
            </motion.div>

            <div className="space-y-4">
              <motion.h3
                className="text-2xl font-bold bg-gradient-to-r from-white to-blue-300 bg-clip-text text-transparent"
                animate={{ opacity: isDragActive ? 0.7 : 1 }}
              >
                {isDragActive ? '🎯 Drop your resume here!' : '📄 Upload Resume for AI Analysis'}
              </motion.h3>

              <motion.p
                className="text-blue-200 text-lg"
                animate={{ opacity: isDragActive ? 0.5 : 1 }}
              >
                Drag and drop your resume, or click to browse
              </motion.p>

              <p className="text-blue-300 text-sm opacity-75">
                Supports PDF, DOC, DOCX files • Max 10MB
              </p>
            </div>

            <motion.button
              className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-4 px-8 rounded-2xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300"
              whileHover={{ scale: 1.05, boxShadow: "0 20px 40px rgba(59, 130, 246, 0.4)" }}
              whileTap={{ scale: 0.95 }}
              type="button"
            >
              <span className="flex items-center space-x-2">
                <SparklesIcon className="w-5 h-5" />
                <span>Choose File</span>
              </span>
            </motion.button>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default FileUpload;
