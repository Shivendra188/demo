import { useState, useRef, useEffect } from "react";
import { sendCommand } from "../services/api";
import { useActivity } from "../context/ActivityContext";

const AGENTS = [
  "Quote Agent",
  "Policy Agent",
  "Policy Data Agent",
  "CRM Agent",
  "Reminder Agent",
];

const AGENT_MAP = {
  QUOTE: "Quote Agent",
  POLICY: "Policy Agent",
  POLICY_DATA: "Policy Data Agent",
  CRM: "CRM Agent",
  REMINDER: "Reminder Agent",
  UNKNOWN: "System",
};

export default function CopilotChat() {
  const { pushActivity } = useActivity(); // ✅ CONTEXT ONLY

  const [messages, setMessages] = useState([
    {
      role: "agent",
      agent: "Copilot",
      content:
        "👋 Hello! I’m your AI Insurance Copilot.\n\nTry:\n• health quote CUST0001\n• policy POL1025\n• policy status POL1025\n• update CUST0001 phone 9876543210\n• send reminders",
      time: new Date().toLocaleTimeString(),
    },
  ]);

  const [activeAgent, setActiveAgent] = useState(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const text = input.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
        time: new Date().toLocaleTimeString(),
      },
    ]);

    setInput("");
    setLoading(true);

    // ✅ ACTIVITY: command received
    pushActivity({
      agent: "Copilot",
      status: "running",
      action: `Command received: ${text}`,
    });

    try {
      const res = await sendCommand(text);

      const taskType = res?.taskType || "UNKNOWN";
      const agentName = AGENT_MAP[taskType] || "AI Agent";
      const responseText =
        res?.response || "✅ Command executed successfully.";

      setActiveAgent(agentName);
      setTimeout(() => setActiveAgent(null), 4000);

      // ✅ ACTIVITY: agent processing
      pushActivity({
        agent: agentName,
        status: "running",
        action: "Processing request",
      });

      // ✅ ACTIVITY: success
      pushActivity({
        agent: agentName,
        status: "success",
        action: responseText,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          agent: agentName,
          content: responseText,
          time: new Date().toLocaleTimeString(),
        },
      ]);
    } catch (err) {
      const errorText =
        err?.message || "Something went wrong while executing the command.";

      // ✅ ACTIVITY: failure
      pushActivity({
        agent: "System",
        status: "failed",
        action: errorText,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          agent: "System",
          content: `❌ ${errorText}`,
          time: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full bg-gradient-to-br from-slate-950 to-slate-900 rounded-2xl overflow-hidden border border-slate-800">
      {/* CHAT */}
      <div className="flex flex-col flex-1">
        <div className="p-5 border-b border-slate-800">
          <h2 className="text-xl font-bold text-white">
            🤖 AI Insurance Copilot
          </h2>
          <p className="text-sm text-slate-400">
            Natural language insurance operations
          </p>
        </div>

        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-xl ${
                m.role === "user" ? "ml-auto text-right" : ""
              }`}
            >
              {m.role === "agent" && (
                <div className="mb-1 text-xs text-amber-400 font-semibold">
                  🤖 {m.agent}
                </div>
              )}

              <div
                className={`p-4 rounded-xl text-sm whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-amber-400 text-black"
                    : "bg-slate-800 text-slate-100"
                }`}
              >
                {m.content}
              </div>

              <span className="text-xs text-slate-500">{m.time}</span>
            </div>
          ))}

          {loading && (
            <div className="text-slate-400 text-sm animate-pulse">
              🤖 AI agent is thinking…
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="p-4 border-t border-slate-800 flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about policies, quotes, CRM, reminders..."
            className="flex-1 px-4 py-3 rounded-xl bg-slate-800 text-white outline-none"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-amber-400 text-black font-semibold disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>

      {/* AGENT STATUS */}
      <div className="w-72 border-l border-slate-800 p-4 bg-slate-950">
        <h3 className="text-sm font-semibold text-white mb-4">
          🧠 AI Agents Status
        </h3>

        {AGENTS.map((agent) => (
          <div
            key={agent}
            className={`mb-3 p-3 rounded-lg text-sm ${
              activeAgent === agent
                ? "bg-amber-400 text-black font-semibold"
                : "bg-slate-900 text-slate-300"
            }`}
          >
            {activeAgent === agent ? "⚡ Active" : "✅ Ready"} — {agent}
          </div>
        ))}

        <div className="mt-6 text-xs text-emerald-400">
          ● Backend connected
        </div>
      </div>
    </div>
  );
}
