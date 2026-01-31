import axios from "axios";

const API_BASE = "http://localhost:8000"; // backend URL

export async function sendChatMessage(message) {
  try {
    const response = await axios.post(`${API_BASE}/chat`, {
      message: message,
    });

    return response.data;
  } catch (error) {
    console.error("Chat API error:", error);
    throw error;
  }
}
