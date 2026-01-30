import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

/* =========================
   Global Error Handler
   ========================= */
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err?.response?.data?.error ||
      err?.response?.data?.detail ||
      err?.message ||
      "Server error";

    // ✅ Always throw Error object
    return Promise.reject(new Error(message));
  }
);

/* =========================
   Copilot / AI Chat API
   ========================= */
export const sendCommand = async (message) => {
  const response = await api.post("/chat", {
    message,
  });
  return response.data;
};

export default api;
