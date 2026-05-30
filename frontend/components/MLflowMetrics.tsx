"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { Network, Cpu, Activity, Clock } from "lucide-react";
import { fetchMLflowStats } from "../services/api";

export default function MLflowMetrics() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMLflowStats().then((data: any) => {
      if (!data.error) setStats(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="h-64 rounded-2xl border border-slate-800 bg-slate-900/40 animate-pulse" />;
  }

  if (!stats) {
    return (
      <motion.div 
        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        className="p-6 rounded-2xl border border-red-800/50 bg-red-900/20 text-red-400 text-center font-medium shadow-lg flex flex-col items-center gap-2"
      >
        <Activity size={24} className="text-red-500 mb-2" />
        <span>⚠️ Cannot reach MLflow data.</span>
        <span className="text-sm text-red-400/80">Did you restart the FastAPI backend after adding the new endpoint?</span>
      </motion.div>
    );
  }

  const metricKeys = Object.keys(stats.metrics);
  const realRmseKey = metricKeys.find(k => k.toLowerCase().includes("rmse") || k.toLowerCase().includes("l2"));
  const rmse = realRmseKey ? stats.metrics[realRmseKey].toFixed(4) : "N/A";
  const learningRate = stats.params["learning_rate"] || "0.05";

  return (
    <motion.section 
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.6 }}
      className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-20"
    >
      <div className="col-span-1 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-md p-6 flex flex-col justify-between shadow-xl">
        <div>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Network className="text-purple-400" /> MLOps Tracking
            </h3>
            <span className="flex items-center gap-1.5 px-3 py-1 bg-purple-500/10 text-purple-400 text-xs font-bold rounded-md border border-purple-500/20 uppercase tracking-wider">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
              MLflow Active
            </span>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center bg-slate-800/30 p-3 rounded-xl border border-slate-700/50 hover:bg-slate-800/50 transition-colors">
              <span className="text-slate-400 text-sm flex items-center gap-2"><Clock size={16}/> Last Trained</span>
              <span className="text-white font-mono text-xs font-semibold">
                {stats.training_date}
              </span>
            </div>
            <div className="flex justify-between items-center bg-slate-800/30 p-3 rounded-xl border border-slate-700/50 hover:bg-slate-800/50 transition-colors">
              <span className="text-slate-400 text-sm flex items-center gap-2"><Activity size={16}/> Validation RMSE</span>
              <span className="text-cyan-400 font-bold">{rmse}</span>
            </div>
            <div className="flex justify-between items-center bg-slate-800/30 p-3 rounded-xl border border-slate-700/50 hover:bg-slate-800/50 transition-colors">
              <span className="text-slate-400 text-sm flex items-center gap-2"><Cpu size={16}/> Learning Rate</span>
              <span className="text-white font-mono">{learningRate}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="col-span-1 lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-md p-6 shadow-xl">
        <h3 className="text-lg font-bold text-white mb-6">Model Feature Importance (Top K)</h3>
        <div className="w-full h-[220px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.feature_importance} layout="vertical" margin={{ top: 0, right: 30, left: 30, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis 
                dataKey="feature" 
                type="category" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: "#94a3b8", fontSize: 12 }} 
                width={120}
              />
              <Tooltip 
                cursor={{ fill: "rgba(30, 41, 59, 0.5)" }}
                contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", color: "#fff" }}
              />
              <Bar dataKey="importance" radius={[0, 4, 4, 0]} barSize={16}>
                {stats.feature_importance.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? "#22d3ee" : index === 1 ? "#3b82f6" : "#475569"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.section>
  );
}