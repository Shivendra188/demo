import { useActivity } from "../context/ActivityContext";

export default function ActivityFeed() {
  const { activityLog } = useActivity();

  const getIcon = (status) => {
    if (status === "success") return "🟢";
    if (status === "running") return "🔵";
    if (status === "failed") return "🔴";
    return "⚡";
  };

  return (
    <div className="h-full bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden">

      {/* Header */}
      <div className="p-4 border-b border-slate-800">
        <h3 className="text-lg font-bold text-white">📊 Activity Feed</h3>
        <p className="text-xs text-slate-400">
          Live execution logs from AI agents
        </p>
      </div>

      {/* Activity List */}
      <div className="p-4 space-y-3 overflow-y-auto max-h-[32rem]">
        {activityLog.length === 0 && (
          <div className="text-center text-slate-500 text-sm py-10">
            No activity yet
          </div>
        )}

        {activityLog.map((a, i) => (
          <div
            key={i}
            className="p-4 rounded-xl bg-slate-900 border border-slate-800"
          >
            <div className="flex items-start gap-3">
              <div className="text-lg">{getIcon(a.status)}</div>

              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-white">
                    🤖 {a.agent}
                  </span>
                  <span className="text-[11px] text-slate-500">
                    {a.time}
                  </span>
                </div>

                <p className="text-xs text-slate-300 mt-1 whitespace-pre-line">
                  {a.action}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-800 text-xs text-emerald-400">
        ● Backend connected
      </div>
    </div>
  );
}
