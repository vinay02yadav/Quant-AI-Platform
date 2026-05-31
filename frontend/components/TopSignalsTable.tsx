"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchTopSignals } from "../services/api";
import { ArrowUpRight, Loader2, Calendar, Target, BrainCircuit, Activity, AlertTriangle, MessageSquare, Info } from "lucide-react";

export default function TopSignalsTable() {
  const [signals, setSignals] = useState<any[]>([]);
  const [metadata, setMetadata] = useState<{ analysis_date: string; target_date: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedTicker, setExpandedTicker] = useState<string | null>(null);

  useEffect(() => {
    fetchTopSignals()
      .then((data: any) => {
        if (data.error) {
          console.error(data.error);
          setLoading(false);
          return;
        }
        setSignals(data.signals || []);
        setMetadata(data.metadata || null);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const enhancedSignals = signals.map((s: any) => {
    const score = Math.round(s.opportunity_score ?? 0);
    const momentumScore = Math.round(s.momentum_score ?? 0);
    const sentimentScore = Math.round(s.sentiment_score ?? 0);
    
    return {
      ...s,
      ticker: s.Stock_symbol,
      forecastRank: Math.round(s.probability_score ?? 0),
      score,
      momentumScore,
      sentimentScore,
      momentum: momentumScore >= 80 ? "Strong" : momentumScore >= 65 ? "Moderate" : "Weak",
      sentiment: sentimentScore >= 75 ? "Positive" : sentimentScore >= 60 ? "Mixed" : "Negative",
      risk: score >= 80 ? "Low" : score >= 65 ? "Medium" : "High"
    };
  });

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  const toggleRow = (ticker: string) => {
    setExpandedTicker(expandedTicker === ticker ? null : ticker);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="space-y-5"
    >
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3 tracking-tight">
            AI Opportunity Engine
            {loading && <Loader2 size={20} className="animate-spin text-cyan-400" />}
          </h2>
          <p className="text-slate-400 text-sm mt-1">Highest-confidence multihop trajectories ranked by cross-sectional analysis.</p>
        </div>

        {metadata && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-700/50 px-3 py-1.5 rounded-lg text-sm text-slate-300">
              <Calendar size={15} className="text-cyan-400" />
              <span>Analysis: <b className="text-white ml-1">{formatDate(metadata.analysis_date)}</b></span>
            </div>
            <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-700/50 px-3 py-1.5 rounded-lg text-sm text-slate-300">
              <Target size={15} className="text-emerald-400" />
              <span>Target: <b className="text-white ml-1">{formatDate(metadata.target_date)}</b></span>
            </div>
          </motion.div>
        )}
      </div>

      {/* TABLE CONTAINER */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 shadow-2xl backdrop-blur-md overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-900/80 border-b border-slate-800">
            <tr className="text-left text-slate-400 font-semibold uppercase tracking-wider text-xs">
              <th className="px-6 py-4">Asset</th>
              <th className="px-6 py-4 hidden sm:table-cell relative group cursor-help">
                <div className="flex items-center gap-1.5">
                  5D FORECAST RANK <Info size={14} className="group-hover:text-cyan-400 transition-colors" />
                </div>
              </th>
              <th className="px-6 py-4 hidden md:table-cell relative group cursor-help">
                <div className="flex items-center gap-1.5">
                  MOMENTUM <Info size={14} className="group-hover:text-cyan-400 transition-colors" />
                </div>
              </th>
              <th className="px-6 py-4 hidden lg:table-cell relative group cursor-help">
                <div className="flex items-center gap-1.5">
                  SENTIMENT <Info size={14} className="group-hover:text-cyan-400 transition-colors" />
                </div>
              </th>
              <th className="px-6 py-4 text-center relative group cursor-help">
                <div className="flex justify-center items-center gap-1.5">
                  FINAL SCORE <Info size={14} className="group-hover:text-cyan-400 transition-colors" />
                </div>
              </th>
            </tr>
          </thead>
          
          <tbody className="divide-y divide-slate-800/60">
            {!loading && enhancedSignals.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                  No signals generated yet. Ensure pipeline is running.
                </td>
              </tr>
            )}

            {enhancedSignals.map((s, i) => (
              <React.Fragment key={i}>
                <tr 
                  onClick={() => toggleRow(s.ticker)}
                  className={`group cursor-pointer transition-colors ${
                    expandedTicker === s.ticker ? "bg-slate-800/60" : "hover:bg-slate-800/40"
                  }`}
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white text-lg">{s.ticker}</span>
                      <ArrowUpRight size={16} className={`transition-transform duration-300 ${expandedTicker === s.ticker ? "rotate-45 text-cyan-400" : "text-slate-500 group-hover:text-cyan-400"}`} />
                    </div>
                    <div className="text-slate-400 font-mono text-xs mt-0.5">
                      ${s.Close.toFixed(2)}
                    </div>
                  </td>

                  <td className="px-6 py-4 w-[250px] hidden sm:table-cell">
                    <div className="flex items-center gap-3">
                      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden relative group-hover/bar">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${s.forecastRank}%` }}
                          transition={{ duration: 1, delay: i * 0.1 }}
                          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500"
                          style={{ width: `${s.forecastRank}%` }}
                        />
                      </div>
                      <span className="font-semibold text-slate-200 w-10 text-right">{s.forecastRank}%</span>
                    </div>
                  </td>

                  <td className="px-6 py-4 hidden md:table-cell">
                    <span className={`font-medium ${s.momentum === 'Strong' ? 'text-emerald-400' : s.momentum === 'Weak' ? 'text-red-400' : 'text-slate-300'}`}>
                      {s.momentum}
                    </span>
                  </td>

                  <td className="px-6 py-4 hidden lg:table-cell">
                    <span className={`font-medium ${s.sentiment === 'Positive' ? 'text-emerald-400' : s.sentiment === 'Negative' ? 'text-red-400' : 'text-slate-300'}`}>
                      {s.sentiment}
                    </span>
                  </td>

                  <td className="px-6 py-4 text-center">
                    <div className="inline-flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-cyan-300 font-bold text-base shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                      {s.score}
                    </div>
                  </td>
                </tr>

                {/* ANIMATED DROPDOWN */}
                <AnimatePresence>
                  {expandedTicker === s.ticker && (
                    <motion.tr 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className="bg-slate-900/90 border-b border-slate-700/50 overflow-hidden"
                    >
                      <td colSpan={5} className="px-0 py-0">
                        <motion.div 
                          initial={{ y: -10 }} 
                          animate={{ y: 0 }} 
                          exit={{ y: -10 }} 
                          className="p-6"
                        >
                          <div className="flex items-center gap-2 mb-4 text-cyan-400">
                            <BrainCircuit size={18} />
                            <h4 className="text-sm font-bold uppercase tracking-wider">AI Scoring Breakdown</h4>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            
                            <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800">
                              <div className="flex items-center justify-between mb-3">
                                <span className="text-slate-400 text-xs font-semibold uppercase flex items-center gap-1"><Activity size={14}/> Ranking Vectors</span>
                              </div>
                              <div className="space-y-2 text-xs">
                                <div className="flex justify-between border-b border-slate-800 pb-1">
                                  <span className="text-slate-400">5D Forecast (40%)</span>
                                  <span className="text-white font-mono">{s.forecastRank}/100</span>
                                </div>
                                <div className="flex justify-between border-b border-slate-800 pb-1">
                                  <span className="text-slate-400">Momentum (20%)</span>
                                  <span className="text-white font-mono">{s.momentumScore}/100</span>
                                </div>
                                <div className="flex justify-between border-b border-slate-800 pb-1">
                                  <span className="text-slate-400">Sentiment (20%)</span>
                                  <span className="text-white font-mono">{s.sentimentScore}/100</span>
                                </div>
                              </div>
                            </div>

                            <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800">
                              <div className="flex items-center justify-between mb-3">
                                <span className="text-slate-400 text-xs font-semibold uppercase flex items-center gap-1"><MessageSquare size={14}/> NLP Sentiment</span>
                                <span className={`text-xs px-2 py-0.5 rounded border ${s.sentiment === 'Positive' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : s.sentiment === 'Negative' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'}`}>{s.sentiment}</span>
                              </div>
                              <p className="text-slate-300 text-xs leading-relaxed">
                                The embedding architecture ranked this asset's news sentiment in the <strong>{s.sentimentScore}th percentile</strong> of the market today.
                              </p>
                            </div>

                            <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800">
                              <div className="flex items-center justify-between mb-3">
                                <span className="text-slate-400 text-xs font-semibold uppercase flex items-center gap-1"><AlertTriangle size={14}/> Market Context</span>
                                <span className={`text-xs px-2 py-0.5 rounded border ${s.risk === 'Low' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'}`}>{s.risk} Risk Profile</span>
                              </div>
                               <p className="text-slate-300 text-xs leading-relaxed">
                                The technical momentum structure is currently ranked in the <strong>{s.momentumScore}th percentile</strong>, dictating behavior relative to the benchmark.
                              </p>
                            </div>

                          </div>
                        </motion.div>
                      </td>
                    </motion.tr>
                  )}
                </AnimatePresence>
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}