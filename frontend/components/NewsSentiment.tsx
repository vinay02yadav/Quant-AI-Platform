"use client";

import { motion } from "framer-motion";
import { MessageSquare, Flame } from "lucide-react";

export default function NewsSentiment() {
  const narratives = [
    { 
      source: "Macro", 
      snippet: "Federal Reserve signals potential rate stabilization...", 
      fullText: "Federal Reserve signals potential rate stabilization following the latest CPI data print, boosting equity market confidence across high-beta assets.",
      sentiment: "Positive" 
    },
    { 
      source: "Tech Sector", 
      snippet: "Semiconductor supply chain faces minor disruptions...", 
      fullText: "Semiconductor supply chain faces minor disruptions in Taiwan foundries, though top-tier firms maintain adequate inventory buffers for Q3.",
      sentiment: "Mixed" 
    },
    { 
      source: "Energy", 
      snippet: "Crude inventories drop sharply ahead of winter demand...", 
      fullText: "Crude inventories drop sharply ahead of projected winter demand spikes, prompting algorithmic accumulation in the energy sector.",
      sentiment: "Positive" 
    },
  ];

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.15 } }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  return (
    <motion.section 
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: "-50px" }}
      variants={container}
      className="rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-md overflow-visible relative z-20"
    >
      <div className="p-6 border-b border-slate-800 flex items-center justify-between">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <MessageSquare className="text-cyan-400" /> NLP Narrative Engine
        </h3>
        <span className="flex items-center gap-1 text-xs font-semibold px-2 py-1 bg-purple-500/10 text-purple-400 rounded-md border border-purple-500/20">
          <Flame size={12} /> Live Embeddings
        </span>
      </div>
      <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        {narratives.map((n, i) => (
          <motion.div 
            key={i} 
            variants={item}
            whileHover={{ y: -5 }}
            className="space-y-3 bg-slate-800/30 p-4 rounded-xl border border-slate-800/50 hover:bg-slate-800/60 transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">{n.source}</span>
              <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${
                n.sentiment === 'Positive' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
              }`}>{n.sentiment}</span>
            </div>
            
            <div className="relative group cursor-help">
              <p className="text-sm text-slate-300 leading-relaxed truncate group-hover:text-cyan-200 transition-colors">
                "{n.snippet}"
              </p>
              
              <div className="absolute left-0 top-6 mt-1 w-[120%] z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div className="bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-2xl leading-relaxed">
                  "{n.fullText}"
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.section>
  );
}