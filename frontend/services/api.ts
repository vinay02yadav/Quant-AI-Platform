import axios from "axios";
import { HealthStatus, ModelInfo, SignalsResponse, MLflowStats } from "../types/types";

const API = axios.create({
  baseURL: "/api",
});

export const fetchTopSignals = async (): Promise<SignalsResponse | { error: string }> => {
  try {
    const response = await API.get("/top-signals");
    return response.data;
  } catch (error: any) {
    return { error: error.message || "Failed to fetch signals" };
  }
};

export const fetchHealth = async (): Promise<HealthStatus> => {
  const response = await API.get("/health");
  return response.data;
};

export const fetchModelInfo = async (): Promise<ModelInfo> => {
  const response = await API.get("/model-info");
  return response.data;
};

export const fetchMLflowStats = async (): Promise<MLflowStats | { error: string }> => {
  try {
    const response = await API.get("/mlflow-stats");
    return response.data;
  } catch (error: any) {
    return { error: error.message || "Failed to fetch MLflow stats" };
  }
};