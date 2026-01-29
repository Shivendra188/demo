import { Routes, Route, Navigate, createContext } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import CopilotChat from "./components/CopilotChat";
import CustomerTable from "./components/CustomerTable";
import AgentsStatus from "./components/AgentsStatus";
import ActivityFeed from "./components/ActivityFeed";

export const ActivityContext = createContext();

export default function App() {
  return (
    <div className="app">
      <Sidebar />

      <main className="center">
        <Routes>
          <Route path="/" element={<Navigate to="/chat" />} />
          <Route path="/chat" element={<CopilotChat />} />
          <Route path="/customers" element={<CustomerTable />} />
          <Route path="/agents" element={<AgentsStatus />} />
          <Route path="/activity" element={<ActivityFeed />} />
        </Routes>
      </main>
    </div>
  );
}
