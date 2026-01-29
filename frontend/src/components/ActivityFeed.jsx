import { useState, useEffect } from 'react';

export default function ActivityFeed({ activities }) {
  const [activityLog, setActivityLog] = useState([]);

  useEffect(() => {
    if (activities) {
      setActivityLog(prev => [activities, ...prev.slice(0, 9)]); // Last 10
    }
  }, [activities]);

  const getIcon = (type) => {
    const icons = {
      QUOTE: '💰',
      POLICY: '📄',
      REMINDER: '📱',
      CRM: '👤',
      unknown: '⚡'
    };
    return icons[type] || '⚡';
  };

  return (
    <div className="card shadow-2xl">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-2xl font-bold">📊 Activity Feed</h3>
          <p className="text-slate-500">Live results from copilot commands</p>
        </div>
        <span className="px-4 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-bold">
          {activityLog.length}
        </span>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {activityLog.map((activity, i) => (
          <div key={i} className="p-6 bg-gradient-to-r from-slate-50 to-indigo-50 rounded-2xl border-l-4 border-indigo-500 hover:shadow-md transition-all">
            <div className="flex items-start gap-4">
              <div className="text-2xl flex-shrink-0">{getIcon(activity.type)}</div>
              
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-slate-900 mb-1 truncate">
                  {activity.type} Agent
                </div>
                <div className="text-sm text-slate-600 mb-2 truncate">
                  "{activity.message}"
                </div>
                <div className="text-sm bg-white p-3 rounded-xl border shadow-sm">
                  {activity.result || "Executed"}
                </div>
                <div className="text-xs text-slate-500 mt-2">
                  {activity.timestamp}
                </div>
              </div>
            </div>
          </div>
        ))}

        {activityLog.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            <div className="text-4xl mb-4">📱</div>
            <p>Send a command in chat to see live results</p>
          </div>
        )}
      </div>
    </div>
  );
}
