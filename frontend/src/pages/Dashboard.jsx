import { useState } from "react";
import CopilotChat from "../components/CopilotChat";
import ActivityFeed from "../components/ActivityFeed";

export default function Dashboard() {
  const [activity, setActivity] = useState(null);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 h-full">
      <div className="xl:col-span-2">
        <CopilotChat onActivity={setActivity} />
      </div>

      <div>
        <ActivityFeed activity={activity} />
      </div>
    </div>
  );
}
