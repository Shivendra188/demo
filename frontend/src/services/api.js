import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
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

    return Promise.reject(new Error(message));
  }
);

/* =========================
   AI Insurance Copilot
   ========================= */
export const sendCommand = async (message) => {
  if (!message || typeof message !== "string") {
    throw new Error("Message must be a non-empty string");
  }

  const { data } = await api.post("/chat", {
    message: message.trim(),
  });

  // ✅ Normalized response (safe for UI + Activity Feed)
  return {
    taskType: data.task_type || "UNKNOWN",
    response: data.response || "No response",
    raw: data, // optional: debugging / logs
  };
};

/* =========================
   WhatsApp API
   ========================= */
export const sendWhatsApp = async ({ phone, message }) => {
  if (!phone || !message) {
    throw new Error("Phone and message are required");
  }

  const { data } = await api.post("/send-reminder", {
    phone,
    message,
  });

  return data; // { status: "sent" }
};

export default api;
