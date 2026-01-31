import { createContext, useContext, useState } from "react";

const ActivityContext = createContext(null);

export function ActivityProvider({ children }) {
  const [activityLog, setActivityLog] = useState([]);

  const pushActivity = (activity) => {
    setActivityLog((prev) => [
      {
        agent: activity.agent || "SYSTEM",
        status: activity.status || "success",
        action: activity.action || "",
        time: new Date().toLocaleTimeString(),
      },
      ...prev,
    ].slice(0, 10));
  };

  return (
    <ActivityContext.Provider value={{ activityLog, pushActivity }}>
      {children}
    </ActivityContext.Provider>
  );
}

export function useActivity() {
  const context = useContext(ActivityContext);

  if (!context) {
    throw new Error("useActivity must be used inside ActivityProvider");
  }

  return context;
}
