import React from "react";
import { motion } from "framer-motion";

export const Spotlight = ({
  className,
  fill = "white",
}: {
  className?: string;
  fill?: string;
}) => {
  return (
    <motion.svg
      className={`animate-pulse ${className}`}
      width="100%"
      height="100%"
      viewBox="0 0 400 400"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 2 }}
    >
      <defs>
        <radialGradient id={`spotlight-${Math.random()}`} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={fill} stopOpacity={0.8} />
          <stop offset="100%" stopColor={fill} stopOpacity={0} />
        </radialGradient>
      </defs>
      <ellipse cx="200" cy="200" rx="150" ry="150" fill={`url(#spotlight-${Math.random()})`} />
    </motion.svg>
  );
};
