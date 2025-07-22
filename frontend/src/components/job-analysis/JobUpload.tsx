import { useCallback } from 'react';
import { useDropzone, Accept } from 'react-dropzone';
import { motion } from 'framer-motion';
import {
  CloudArrowUpIcon,
  PhotoIcon,
  DocumentIcon,
  XMarkIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface JobUploadProps {
  fileType: 'image' | 'pdf';
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

const JobUpload = ({ fileType, onFileSelect, selectedFile }: JobUploadProps) => {
  // Fix the accept types to match Accept interface
  const acceptedTypes: Accept = fileType === 'image'
    ? { 'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'] }
    : { 'application/pdf': ['.pdf'] };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false
  });

  const removeFile = () => {
    onFileSelect(null as any);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = () => {
    return fileType === 'image' ? PhotoIcon : DocumentIcon;
  };

  if (selectedFile) {
    const FileIcon = getFileIcon();

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-blue-500 rounded-2xl flex items-center justify-center shadow-xl">
              <FileIcon className="w-8 h-8 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-lg">{selectedFile.name}</h3>
              <p className="text-blue-200">{formatFileSize(selectedFile.size)}</p>
              <div className="flex items-center mt-2 space-x-1">
                <CheckCircleIcon className="w-4 h-4 text-green-400" />
                <span className="text-xs text-green-300">Ready for analysis</span>
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
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div
        {...getRootProps()}
        className={`
          relative cursor-pointer transition-all duration-500 transform
          ${isDragActive ? 'scale-105' : 'hover:scale-[1.02]'}
        `}
      >
        <input {...getInputProps()} />

        {/* Glow effects */}
        <div className={`absolute -inset-4 bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 rounded-3xl blur-xl opacity-30 transition-opacity duration-500 ${
          isDragActive ? 'opacity-70' : 'opacity-30'
        }`}></div>

        {/* Main upload area */}
        <div className="relative glass-card p-12 text-center">
          {/* Floating particles */}
          <div className="absolute inset-0 overflow-hidden rounded-3xl">
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-purple-400 rounded-full"
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
              <CloudArrowUpIcon className="w-24 h-24 text-purple-300 mx-auto mb-6 filter drop-shadow-xl" />
              {isDragActive && (
                <motion.div
                  className="absolute inset-0 bg-purple-400 rounded-full blur-xl opacity-50"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              )}
            </motion.div>

            <div className="space-y-4">
              <motion.h3
                className="text-2xl font-bold bg-gradient-to-r from-white to-purple-300 bg-clip-text text-transparent"
                animate={{ opacity: isDragActive ? 0.7 : 1 }}
              >
                {isDragActive
                  ? '🎯 Drop your job posting here!'
                  : `📄 Upload ${fileType === 'image' ? 'Image' : 'PDF'} of Job Posting`
                }
              </motion.h3>

              <motion.p
                className="text-purple-200 text-lg"
                animate={{ opacity: isDragActive ? 0.5 : 1 }}
              >
                {fileType === 'image'
                  ? 'Screenshot or photo of job posting'
                  : 'PDF document containing job details'
                }
              </motion.p>

              <p className="text-purple-300 text-sm opacity-75">
                {fileType === 'image'
                  ? 'Supports JPG, PNG, GIF • Max 10MB'
                  : 'Supports PDF files • Max 10MB'
                }
              </p>
            </div>

            <motion.button
              className="mt-8 bg-gradient-to-r from-purple-500 to-blue-600 text-white font-semibold py-4 px-8 rounded-2xl shadow-2xl hover:shadow-purple-500/25 transition-all duration-300"
              whileHover={{ scale: 1.05, boxShadow: "0 20px 40px rgba(147, 51, 234, 0.4)" }}
              whileTap={{ scale: 0.95 }}
              type="button"
            >
              <span className="flex items-center space-x-2">
                {fileType === 'image' ? (
                  <PhotoIcon className="w-5 h-5" />
                ) : (
                  <DocumentIcon className="w-5 h-5" />
                )}
                <span>Select {fileType === 'image' ? 'Image' : 'PDF'}</span>
              </span>
            </motion.button>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default JobUpload;
