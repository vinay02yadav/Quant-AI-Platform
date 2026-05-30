"use client";

import { motion } from "framer-motion";
import { TrendingUp, Activity, BarChart2 } from "lucide-react";

export default function MarketOverview() {
  const metrics = [
    { label: "SPY (S&P 500)", value: "$598.42", change: "+1.24%", isUp: true, icon: TrendingUp },
    { label: "QQQ (Nasdaq)", value: "$432.10", change: "+1.85%", isUp: true, icon: TrendingUp },
    { label: "VIX (Volatility)", value: "14.25", change: "-5.30%", isUp: false, icon: Activity },
    { label: "Market Sentiment", value: "Bullish", change: "78 / 100 Index", isUp: true, icon: BarChart2 },
  ];

  // Grid container stagger sequence
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { 
        staggerChildren: 0.08,
        delayChildren: 0.45 // Begins right as the hero description settles
      }
    }
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.98 },
    show: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { type: "spring", stiffness: 260, damping: 22 } 
    }
  };

  return (
    <motion.section 
      variants={containerVariants} 
      initial="hidden" 
      animate="show" 
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-2"
    >
      {metrics.map((m, i) => (
        <motion.div 
          key={i} 
          variants={cardVariants}
          whileHover={{ 
            y: -4, 
            borderColor: "rgba(51, 65, 85, 0.7)",
            boxShadow: "0 12px 40px -12px rgba(0,0,0,0.7)"
          }}
          whileTap={{ scale: 0.99 }}
          className="p-6 rounded-xl border border-slate-900 bg-slate-950/40 backdrop-blur-md transition-colors duration-200 group cursor-pointer"
        >
          <div className="flex justify-between items-start mb-4">
            <span className="text-xs font-bold text-slate-400 tracking-wider uppercase">{m.label}</span>
            <div className={`p-2 rounded-lg transition-transform duration-300 group-hover:scale-110 ${
              m.isUp ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
            }`}>
              <m.icon size={16} />
            </div>
          </div>
          
          <div className="flex flex-col space-y-1">
            <span className="text-2xl font-bold tracking-tight text-white group-hover:text-cyan-400 transition-colors duration-200">
              {m.value}
            </span>
            <span className={`text-xs font-semibold tracking-wide ${
              m.isUp ? 'text-emerald-400' : 'text-red-400'
            }`}>
              {m.change}
            </span>
          </div>
        </motion.div>
      ))}
    </motion.section>
  );
}