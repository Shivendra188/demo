import React, { useState, useEffect } from "react";
import api from "../services/api.js";

function StatusBadge({ status }) {
  const baseClasses = "px-3 py-1 rounded-full text-xs font-semibold";

  const statusClasses =
    status === "Active"
      ? "bg-green-100 text-green-600"
      : status === "Expired"
      ? "bg-red-100 text-red-600"
      : "bg-yellow-100 text-yellow-600";

  return <span className={`${baseClasses} ${statusClasses}`}>{status}</span>;
}

export default function CustomerTable() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await api.get("/crm-dashboard");
      setData(response.data.data || []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch CRM data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000000); // 5s refresh
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="card">⏳ Loading CRM...</div>;
  if (error) return <div className="card text-red-500">Error: {error}</div>;

  return (
    <div className="card">
      <h3 className="mb-3 text-lg font-semibold">Customer Management</h3>

      {data.length === 0 ? (
        <p className="text-gray-400">
          No customer data available. Trigger an AI action to load customers.
        </p>
      ) : (
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="text-yellow-300">
              <th className="text-left px-2 py-2 font-semibold">Customer</th>
              <th className="text-left px-2 py-2 font-semibold">Contact</th>
              <th className="text-left px-2 py-2 font-semibold">Policy Type</th>
              <th className="text-left px-2 py-2 font-semibold">Policy ID</th>
              <th className="text-left px-2 py-2 font-semibold">Status</th>
            </tr>
          </thead>

          <tbody>
            {data.map((c, i) => (
              <tr key={i} className="border-t border-yellow-400/25">
                <td className="px-2 py-2">{c.name}</td>
                <td className="px-2 py-2">{c.phone}</td>
                <td className="px-2 py-2">{c.policy_type}</td>
                <td className="px-2 py-2">{c.policy_id}</td>
                <td className="px-2 py-2">
                  <StatusBadge status={c.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
