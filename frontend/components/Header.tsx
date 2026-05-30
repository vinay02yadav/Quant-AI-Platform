"use client";

import { motion } from "framer-motion";
import { Activity } from "lucide-react";

export default function Header() {
  return (
    <motion.header 
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <motion.div 
            whileHover={{ scale: 1.05, rotate: 5 }}
            className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.3)] cursor-pointer"
          >
            <span className="text-white font-bold text-sm">AI</span>
          </motion.div>
          <h1 className="text-lg font-bold text-slate-200 tracking-wide">
            Finance AI Platform
          </h1>
        </div>
        
        <motion.div 
          whileHover={{ scale: 1.05 }}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 cursor-default"
        >
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
            <Activity size={12} /> Pipeline Active
          </span>
        </motion.div>
      </div>
    </motion.header>
  );
}