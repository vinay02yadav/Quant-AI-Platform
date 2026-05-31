"use client";

import { motion } from "framer-motion";
import { Radio } from "lucide-react";

export default function HeroSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { duration: 0.8, type: "spring", stiffness: 100, damping: 20 } 
    }
  };

  return (
    <motion.section 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="relative pt-20 pb-12 flex flex-col items-center justify-center text-center overflow-visible"
    >
      {/* Animated Aurora Spotlight Background */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 0.15, scale: 1 }}
        transition={{ duration: 2, ease: "easeOut" }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 blur-[100px] pointer-events-none rounded-full"
      />

      {/* Live Status Pill */}
      <motion.div 
        variants={itemVariants} 
        whileHover={{ scale: 1.02, boxShadow: "0px 0px 20px rgba(6, 182, 212, 0.3)" }}
        className="relative z-10 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-900/90 border border-cyan-900/50 mb-10 backdrop-blur-md shadow-[0_8px_32px_rgba(0,0,0,0.5)] cursor-default transition-all duration-300"
      >
        <div className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
        </div>
        <Radio size={14} className="text-cyan-400 hidden" />
        <span className="text-xs font-bold text-slate-200 tracking-widest uppercase">Live Market Pulse Active</span>
        <span className="mx-1 text-slate-700">|</span>
        <span className="text-xs font-bold text-purple-400 tracking-widest uppercase drop-shadow-md">Regime: High Volatility</span>
      </motion.div>

      {/* Bulletproof Title Block */}
      <motion.h1 
        variants={itemVariants}
        className="relative z-10 text-5xl md:text-7xl lg:text-8xl font-black mb-8 tracking-tight py-4 leading-tight flex flex-wrap justify-center gap-x-4"
      >
        <span className="text-white drop-shadow-sm">Quantitative</span>
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 drop-shadow-sm">
          Intelligence
        </span>
      </motion.h1>
      
      {/* Subtitle / Description */}
      <motion.p 
        variants={itemVariants}
        className="relative z-10 max-w-2xl text-lg text-slate-400 leading-relaxed font-medium px-4"
      >
        Autonomous multi-horizon predictions powered by LightGBM and NLP sentiment embeddings. Actionable signals extracted from market noise.
      </motion.p>
    </motion.section>
  );
}