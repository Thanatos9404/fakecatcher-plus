import type { ReactNode } from 'react';
import { ToastContainer } from 'react-toastify';
import { BackgroundBeams } from '../ui/background-beams';
import { Spotlight } from '../ui/spotlight';
import { motion } from 'framer-motion';
import 'react-toastify/dist/ReactToastify.css';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <BackgroundBeams className="z-0" />
      <Spotlight className="absolute top-0 left-1/4 z-10" fill="rgba(59, 130, 246, 0.3)" />
      <Spotlight className="absolute bottom-0 right-1/4 z-10" fill="rgba(147, 51, 234, 0.3)" />

      {/* Content */}
      <div className="relative z-20">
        {/* Header */}
        <motion.header
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="bg-black/20 backdrop-blur-xl border-b border-white/10"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <motion.div
                className="flex items-center space-x-4"
                whileHover={{ scale: 1.05 }}
              >
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl">
                  <motion.span
                    className="text-white font-bold text-xl"
                    animate={{ rotate: [0, 360] }}
                    transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                  >
                    F+
                  </motion.span>
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-blue-300 bg-clip-text text-transparent">
                    FakeCatcher++
                  </h1>
                  <p className="text-blue-200 text-sm">AI-Powered Authenticity Verification</p>
                </div>
              </motion.div>

              <motion.div
                className="flex items-center space-x-2 bg-green-500/20 backdrop-blur-sm px-4 py-2 rounded-full border border-green-400/30"
                animate={{
                  boxShadow: [
                    "0 0 20px rgba(34, 197, 94, 0.3)",
                    "0 0 40px rgba(34, 197, 94, 0.6)",
                    "0 0 20px rgba(34, 197, 94, 0.3)"
                  ]
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-200">MVP 1 - Resume Analysis</span>
              </motion.div>
            </div>
          </div>
        </motion.header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            {children}
          </motion.div>
        </main>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="bg-black/10 backdrop-blur-xl border-t border-white/10 py-8"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center text-blue-200">
              <p className="mb-2">FakeCatcher++ v1.0 - Fighting fake content in recruitment</p>
              <p className="text-xs text-blue-300">⚠️ This tool provides advisory analysis - not legal validation</p>
            </div>
          </div>
        </motion.footer>
      </div>

      {/* Toast Notifications */}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
        toastStyle={{
          background: 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: 'white'
        }}
      />
    </div>
  );
};

export default Layout;
