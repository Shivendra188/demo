import { useEffect, useState } from "react";
import { useActivity } from "../context/ActivityContext";

const AGENTS = ["QUOTE", "POLICY", "POLICY_DATA", "CRM", "REMINDER"];

export default function AgentsStatus() {
  const { lastTaskType, totalTasks } = useActivity();
  const [activeAgent, setActiveAgent] = useState(null);

  useEffect(() => {
    if (lastTaskType) {
      setActiveAgent(lastTaskType);
      const timer = setTimeout(() => setActiveAgent(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [lastTaskType]);

  return (
    <div className="card">
      <h3 className="mb-4 text-lg font-semibold">🤖 AI Agents</h3>

      <div className="space-y-3">
        {AGENTS.map((agent) => {
          const isActive = activeAgent === agent;

          return (
            <div
              key={agent}
              className={`flex items-center justify-between px-4 py-3 rounded-xl border ${
                isActive
                  ? "bg-amber-400 text-black border-amber-300"
                  : "bg-slate-900 border-slate-700 text-slate-300"
              }`}
            >
              <span className="font-medium">{agent} Agent</span>
              <span className="text-sm font-semibold">
                {isActive ? "🟢 Active" : "⚪ Idle"}
              </span>
            </div>
          );
        })}
      </div>

      <div className="mt-6 grid grid-cols-3 gap-3 text-center text-sm">
        <div className="p-3 bg-slate-900 rounded-xl">
          <div className="text-slate-400">Agents</div>
          <div className="text-lg font-bold text-white">{AGENTS.length}</div>
        </div>

        <div className="p-3 bg-slate-900 rounded-xl">
          <div className="text-slate-400">Tasks</div>
          <div className="text-lg font-bold text-white">{totalTasks}</div>
        </div>

        <div className="p-3 bg-slate-900 rounded-xl">
          <div className="text-slate-400">Avg Time</div>
          <div className="text-lg font-bold text-white">~1.2s</div>
        </div>
      </div>
    </div>
  );
}
