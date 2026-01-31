import { useState } from "react";
import { sendWhatsApp } from "../api/api";

export default function SendWhatsApp({ phone, text }) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const handleSend = async () => {
    try {
      setLoading(true);
      setStatus("");

      await sendWhatsApp(phone, text);

      setStatus("✅ Message sent");
    } catch (err) {
      setStatus("❌ Failed to send");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-2">
      <button
        onClick={handleSend}
        disabled={loading}
        className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
      >
        {loading ? "Sending..." : "📲 Send WhatsApp"}
      </button>

      {status && (
        <p className="text-xs mt-1 text-slate-400">{status}</p>
      )}
    </div>
  );
}
