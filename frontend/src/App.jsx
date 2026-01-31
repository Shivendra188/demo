import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import CopilotChat from "./components/CopilotChat";
import CustomerTable from "./components/CustomerTable";
import AgentsStatus from "./components/AgentsStatus";
import ActivityFeed from "./components/ActivityFeed";
import Dashboard from "./pages/Dashboard";
import { ActivityProvider } from "./context/ActivityContext";

export default function App() {
  return (
    <ActivityProvider>
      <div className="app">
        <Sidebar />

        <main className="center">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<CopilotChat />} />
            <Route path="/customers" element={<CustomerTable />} />
            <Route path="/agents" element={<AgentsStatus />} />
            <Route path="/activity" element={<ActivityFeed />} />
          </Routes>
        </main>
      </div>
    </ActivityProvider>
  );
}
