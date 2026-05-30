import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import MarketOverview from "@/components/MarketOverview";
import TopSignalsTable from "@/components/TopSignalsTable";
import NewsSentiment from "@/components/NewsSentiment";
import ModelAnalytics from "@/components/ModelAnalytics";
import StrategyPerformance from "@/components/StrategyPerformance";
import MLflowMetrics from "@/components/MLflowMetrics"; 

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 selection:bg-cyan-500/30 font-sans">
      
      {/* Background Ambient Glow */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-900/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] rounded-full bg-blue-900/10 blur-[100px]" />
      </div>

      <Header />

      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12 pb-20">
        
        <HeroSection />
        <MarketOverview />
        
        <section id="ai-engine">
          <TopSignalsTable />
        </section>

        <NewsSentiment />
        
        <StrategyPerformance />

        {/* The new MLflow Tracking Section */}
        <MLflowMetrics />

        <ModelAnalytics />

      </main>
    </div>
  );
}