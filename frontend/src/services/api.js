import axios from "axios";

const API_BASE = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000, // 10s timeout
  headers: {
    "Content-Type": "application/json",
  },
});

export async function sendCommand(message) {
  try {
    const response = await api.post("/chat", { message });
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    throw new Error(error.response?.data?.error || "Backend unavailable");
  }
}

export async function getQuotes(type) {
  const response = await api.get(`/quotes/${type}`);
  return response.data.quotes;
}

export async function getDashboard() {
  const response = await api.get("/crm-dashboard");
  return response.data;
}

export default api;
