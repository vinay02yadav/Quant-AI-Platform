export interface Signal {
  Date: string;
  Stock_symbol: string;
  Close: number;
  buy_probability: number;
  signal?: number;
  probability_score?: number;
  momentum_score?: number;
  sentiment_score?: number;
  regime_score?: number;
  opportunity_score?: number;
}

export interface HealthStatus {
  status: string;
  device: string;
}

export interface ModelInfo {
  model: string;
  sequence_length: number;
  features: number;
  device: string;
  checkpoint: string;
}

export interface SignalsResponse {
  signals: Signal[];
  metadata: {
    analysis_date: string;
    target_date: string;
  } | null;
}

export interface MLflowStats {
  run_id: string;
  status: string;
  training_date: string;
  metrics: Record<string, number>;
  params: Record<string, string>;
  feature_importance: { feature: string; importance: number }[];
}