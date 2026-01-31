import React, { useState, useEffect } from "react";
import api, { sendWhatsApp } from "../services/api";

/* ===== Status Badge ===== */
function StatusBadge({ status }) {
  const base = "px-3 py-1 rounded-full text-xs font-semibold";

  const color =
    status === "Active"
      ? "bg-green-100 text-green-700"
      : status === "Expired"
      ? "bg-red-100 text-red-700"
      : "bg-yellow-100 text-yellow-700";

  return <span className={`${base} ${color}`}>{status}</span>;
}

/* ===== Customer Table ===== */
export default function CustomerTable() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sending, setSending] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      // ✅ Use Axios baseURL
      const { data } = await api.get("/crm-dashboard");

      setRows(data?.data || []);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch CRM data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  /* ===== WhatsApp ===== */
  const sendReminder = async (row) => {
    try {
      setSending(row.policy_id);

      await sendWhatsApp({
        phone: row.phone,
        message: `Hello ${row.name}, your ${row.policy_type} policy (${row.policy_id}) is ${row.status}. Please contact us for assistance.`,
      });

      alert("✅ WhatsApp message sent");
    } catch (err) {
      alert("❌ Failed to send WhatsApp");
    } finally {
      setSending(null);
    }
  };

  if (loading) return <div className="card">⏳ Loading CRM...</div>;
  if (error) return <div className="card text-red-500">{error}</div>;

  return (
    <div className="card">
      <h3 className="mb-4 text-lg font-semibold text-white">
        👥 Customer Management
      </h3>

      {rows.length === 0 ? (
        <p className="text-gray-400">No customer data available.</p>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="text-yellow-300 border-b border-yellow-400/30">
              <th className="text-left px-2 py-2">Customer</th>
              <th className="text-left px-2 py-2">Phone</th>
              <th className="text-left px-2 py-2">Policy Type</th>
              <th className="text-left px-2 py-2">Policy ID</th>
              <th className="text-left px-2 py-2">Status</th>
              <th className="text-left px-2 py-2">Action</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((c, i) => (
              <tr
                key={i}
                className="border-t border-yellow-400/20 hover:bg-slate-900/40"
              >
                <td className="px-2 py-2">{c.name}</td>
                <td className="px-2 py-2">{c.phone || "N/A"}</td>
                <td className="px-2 py-2">{c.policy_type}</td>
                <td className="px-2 py-2">{c.policy_id}</td>
                <td className="px-2 py-2">
                  <StatusBadge status={c.status || "Active"} />
                </td>
                <td className="px-2 py-2">
                  <button
                    disabled={!c.phone || sending === c.policy_id}
                    onClick={() => sendReminder(c)}
                    className={`text-xs px-3 py-1 rounded-lg font-semibold
                      ${
                        !c.phone
                          ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                          : "bg-emerald-600 hover:bg-emerald-500 text-white"
                      }`}
                  >
                    {sending === c.policy_id ? "Sending…" : "WhatsApp"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
