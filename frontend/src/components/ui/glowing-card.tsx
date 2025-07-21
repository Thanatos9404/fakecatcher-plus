import { motion } from "framer-motion";
import { ReactNode } from "react";

interface GlowingCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: string;
}

export const GlowingCard = ({
  children,
  className = "",
  glowColor = "blue"
}: GlowingCardProps) => {
  return (
    <motion.div
      className={`relative group ${className}`}
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300 }}
    >
      {/* Glow effect */}
      <div className={`absolute -inset-1 bg-gradient-to-r from-${glowColor}-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200`}></div>

      {/* Card content */}
      <div className="relative glass-card">
        {children}
      </div>
    </motion.div>
  );
};
