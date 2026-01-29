import { useState, useEffect, useRef, useCallback } from "react";
import { sendCommand } from "../services/api";

export default function CopilotChat() {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "agent",
      content: "Hello! I'm your AI insurance copilot. I can help you analyze policies, process claims, update customer information, and automate workflows. How can I assist you today? \nTry: 'health quote CUST0001' | 'policy POL1001' | 'send reminders' | 'update CUST0001 phone 9876543210'",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Send message
  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = {
      id: Date.now(),
      role: "user",
      content: input.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    // Optimistic UI
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setError(null);
    setInput("");

    try {
      const response = await sendCommand(userMsg.content);
      
      const agentMsg = {
        id: `agent-${Date.now()}`,
        role: "agent",
        content: response.response || "✅ Command executed! Check dashboard.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      
      setMessages(prev => [...prev, agentMsg]);
    } catch (err) {
      const errorMsg = {
        id: `error-${Date.now()}`,
        role: "agent",
        content: `❌ ${err.message}\nTry: npm run dev + uvicorn backend running`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorMsg]);
      setError(err.message);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // Enter key + Cmd+Enter
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="w-screen max-w-2xl mx-auto from-slate-900 to-slate-800 rounded-3xl shadow-2xl overflow-hidden border border-slate-700">
      
      {/* Header */}
      <div className="bg-linear-to-r from-amber-400 to-amber-500 p-6">
        <h2 className="text-2xl font-black mb-1 text-black">🤖 Insurance Copilot</h2>
        <p className="text-black text-sm">GenAI Agents: Quotes • Policies • Reminders • CRM</p>
      </div>

      {/* Messages */}
      <div className="h-96 md:h-100 p-6 overflow-y-auto bg-slate-900/50 backdrop-blur-sm space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "agent" ? "justify-start" : "justify-end"}`}
          >
            <div
              className={`max-w-xs md:max-w-md p-4 rounded-2xl shadow-lg ${
                msg.role === "agent"
                  ? "bg-linear-to-r from-yellow-400 to-yellow-500 text-black rounded-br-2xl"
                  : "bg-white text-slate-900 rounded-bl-2xl"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              <span className={`text-xs mt-2 block opacity-75 ${
                msg.role === "agent" ? "text-black" : "text-slate-500"
              }`}>
                {msg.timestamp}
              </span>
            </div>
          </div>
        ))}
        
        {/* Loading */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-linear-to-r from-amber-400 to-amber-500 max-w-xs animate-pulse">
              <div className="h-4 g-gradient-to-r from-amber-400 to-amber-500 w-3/4 mb-2"></div>
              <div className="h-4 g-gradient-to-r from-amber-400 to-amber-500 w-1/2"></div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 border-t border-slate-700 bg-slate-900/50">
        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-xl text-red-100 text-sm">
            {error}
          </div>
        )}
        <div className="flex gap-3">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="💬 'health quote CUST0001' or 'send reminders'..."
            className="flex-1 px-6 py-4 bg-slate-800/50 border border-slate-600 rounded-2xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-300 focus:border-transparent resize-none"
            disabled={loading}
            autoFocus
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="px-8 py-4 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 disabled:opacity-50 font-bold rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 whitespace-nowrap text-slate-900"
          >
            {loading ? "⏳" : "➤ Send"}
          </button>
        </div>
        
      </div>
    </div>
  );
}
