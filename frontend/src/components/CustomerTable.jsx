import React, { useState, useEffect } from "react";
import api from "../services/api.js";

/* ===== Status Badge ===== */
function StatusBadge({ status }) {
  const baseClasses = "px-3 py-1 rounded-full text-xs font-semibold";

  const statusClasses =
    status === "Active"
      ? "bg-green-100 text-green-700"
      : status === "Expired"
      ? "bg-red-100 text-red-700"
      : "bg-yellow-100 text-yellow-700";

  return <span className={`${baseClasses} ${statusClasses}`}>{status}</span>;
}

/* ===== Customer Table ===== */
export default function CustomerTable() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const res = await api.get("/crm-dashboard");

      // Backend returns { data: [], total, updated }
      setRows(res.data?.data ?? []);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch CRM data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // refresh every 30 seconds (safe for production)
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="card">⏳ Loading CRM...</div>;
  if (error) return <div className="card text-red-500">{error}</div>;

  return (
    <div className="card">
      <h3 className="mb-3 text-lg font-semibold">Customer Management</h3>

      {rows.length === 0 ? (
        <p className="text-gray-400">
          No customer data available. Trigger an AI action to load customers.
        </p>
      ) : (
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="text-yellow-300">
              <th className="text-left px-2 py-2">Customer</th>
              <th className="text-left px-2 py-2">Phone</th>
              <th className="text-left px-2 py-2">Policy Type</th>
              <th className="text-left px-2 py-2">Policy ID</th>
              <th className="text-left px-2 py-2">Status</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((c, i) => (
              <tr key={i} className="border-t border-yellow-400/25">
                <td className="px-2 py-2">{c.name}</td>
                <td className="px-2 py-2">{c.phone}</td>
                <td className="px-2 py-2">{c.policy_type}</td>
                <td className="px-2 py-2">{c.policy_id}</td>
                <td className="px-2 py-2">
                  <StatusBadge status={c.status || "Active"} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
