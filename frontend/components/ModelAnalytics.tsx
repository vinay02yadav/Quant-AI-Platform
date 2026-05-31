"use client";

import { motion } from "framer-motion";
import { Cpu, Database, Network } from "lucide-react";

export default function ModelAnalytics() {
  // FIX: Added ': any' to bypass TS errors for both animation containers
  const container: any = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.2 } }
  };

  const item: any = {
    hidden: { opacity: 0, scale: 0.9 },
    show: { opacity: 1, scale: 1, transition: { type: "spring", stiffness: 300 } }
  };

  return (
    <motion.section 
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: "-20px" }}
      variants={container}
      className="grid grid-cols-1 md:grid-cols-3 gap-4"
    >
      <motion.div variants={item} className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 flex items-center gap-4 hover:bg-slate-800/40 transition-colors">
        <div className="p-3 bg-slate-800 rounded-xl text-slate-400 shadow-inner"><Cpu size={24} /></div>
        <div>
          <p className="text-xs text-slate-500 uppercase font-semibold">Model Architecture</p>
          <p className="text-sm font-mono text-white mt-0.5">LightGBM MultiOutput</p>
        </div>
      </motion.div>
      
      <motion.div variants={item} className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 flex items-center gap-4 hover:bg-slate-800/40 transition-colors">
        <div className="p-3 bg-slate-800 rounded-xl text-slate-400 shadow-inner"><Database size={24} /></div>
        <div>
          <p className="text-xs text-slate-500 uppercase font-semibold">Data Pipeline</p>
          <p className="text-sm font-mono text-white mt-0.5">102 Features (Multimodal)</p>
        </div>
      </motion.div>

      <motion.div variants={item} className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 flex items-center gap-4 hover:bg-slate-800/40 transition-colors">
        <div className="p-3 bg-slate-800 rounded-xl text-slate-400 shadow-inner"><Network size={24} /></div>
        <div>
          <p className="text-xs text-slate-500 uppercase font-semibold">Inference Latency</p>
          <p className="text-sm font-mono text-white mt-0.5">~120ms / Batch</p>
        </div>
      </motion.div>
    </motion.section>
  );
}