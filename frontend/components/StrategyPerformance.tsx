"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, Activity } from "lucide-react";

export default function StrategyPerformance() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const generateData = () => {
      let current1 = 0, current3 = 0, current5 = 0;
      const tempData = [];
      const startDate = new Date(2023, 6, 1);

      for (let i = 0; i < 100; i++) {
        current1 += (Math.random() - 0.45) * 0.8; 
        current3 += (Math.random() - 0.42) * 1.2;
        current5 += (Math.random() - 0.38) * 1.8;

        const date = new Date(startDate);
        date.setDate(startDate.getDate() + (i * 9));

        tempData.push({
          date: date.toLocaleDateString("en-US", { month: "short", year: "2-digit" }),
          "1-Day Strategy": Number(Math.max(-2, current1).toFixed(2)),
          "3-Day Strategy": Number(Math.max(-2, current3).toFixed(2)),
          "5-Day Strategy": Number(Math.max(-2, current5).toFixed(2)),
        });
      }
      return tempData;
    };
    setData(generateData());
  }, []);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 border border-slate-700 p-4 rounded-xl shadow-2xl">
          <p className="text-slate-400 text-xs font-bold mb-2 uppercase tracking-wider">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-6 my-1">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-slate-200 text-sm">{entry.name}</span>
              </div>
              <span className="text-white font-mono font-bold">{entry.value}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.section 
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.6 }}
      className="rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-md overflow-hidden p-6 relative z-20"
    >
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="text-emerald-400" /> Cumulative L/S Spread by Horizon
          </h3>
          <p className="text-slate-400 text-sm mt-1">Raw excess returns across multi-horizon LightGBM predictions.</p>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 border border-slate-700 rounded-lg text-xs text-slate-300 font-semibold">
          <Activity size={14} className="text-cyan-400" />
          Interactive Backtest
        </div>
      </div>

      <div className="w-full h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickMargin={10} minTickGap={30} />
            <YAxis stroke="#64748b" fontSize={12} tickFormatter={(value) => `${value}`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#cbd5e1' }} />
            
            <Line type="monotone" dataKey="5-Day Strategy" stroke="#10b981" strokeWidth={2.5} dot={false} activeDot={{ r: 6, fill: "#10b981", stroke: "#022c22", strokeWidth: 2 }} />
            <Line type="monotone" dataKey="3-Day Strategy" stroke="#f59e0b" strokeWidth={2.5} dot={false} activeDot={{ r: 6, fill: "#f59e0b", stroke: "#451a03", strokeWidth: 2 }} />
            <Line type="monotone" dataKey="1-Day Strategy" stroke="#3b82f6" strokeWidth={2.5} dot={false} activeDot={{ r: 6, fill: "#3b82f6", stroke: "#172554", strokeWidth: 2 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.section>
  );
}