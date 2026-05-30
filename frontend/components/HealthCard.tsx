"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity } from "lucide-react";
import { fetchHealth } from "../services/api";

export default function HealthCard() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(console.error);
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, type: "spring", stiffness: 200 }}
      className="bg-slate-900/50 backdrop-blur-xl rounded-3xl p-6 border border-slate-800 shadow-xl flex flex-col justify-between h-full"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-emerald-500/10 rounded-lg shadow-inner">
          <Activity size={20} className="text-emerald-400" />
        </div>
        <h2 className="text-xl font-semibold text-white tracking-tight">System Health</h2>
      </div>

      <AnimatePresence mode="wait">
        {health ? (
          <motion.div 
            key="loaded"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4 text-sm sm:text-base"
          >
            <div className="flex justify-between items-center bg-slate-800/30 p-3 rounded-xl border border-slate-700/50 hover:bg-slate-800/50 transition-colors">
              <span className="text-slate-400 font-medium">API Status</span>
              <span className="flex items-center gap-2 text-emerald-400 font-bold bg-emerald-400/10 px-3 py-1 rounded-full text-xs tracking-wider">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                {health.status.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between items-center bg-slate-800/30 p-3 rounded-xl border border-slate-700/50 hover:bg-slate-800/50 transition-colors">
              <span className="text-slate-400 font-medium">Compute Device</span>
              <span className="text-white font-mono text-xs font-semibold bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
                {health.device.toUpperCase()}
              </span>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            <div className="h-12 bg-slate-800/50 rounded-xl w-full animate-pulse" />
            <div className="h-12 bg-slate-800/50 rounded-xl w-full animate-pulse" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}