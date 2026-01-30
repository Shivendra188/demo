// import { useState } from "react";
// import { sendChatMessage } from "../services/chatService";

// export default function Chat() {
//   const [message, setMessage] = useState("");
//   const [reply, setReply] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState("");

//   const handleSend = async () => {
//     if (!message.trim()) return;

//     try {
//       setLoading(true);
//       setError("");

//       const res = await sendChatMessage({
//         message,
//       });

//       setReply(`${res.agent}: ${res.response}`);
//       setMessage("");
//     } catch (err) {
//       setError(err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="card">
//       <h3>AI Assistant</h3>

//       <textarea
//         value={message}
//         onChange={(e) => setMessage(e.target.value)}
//         placeholder="Ask about policy, quote, CRM, reminder..."
//       />

//       <button onClick={handleSend} disabled={loading}>
//         {loading ? "Thinking..." : "Send"}
//       </button>

//       {reply && <div className="response">{reply}</div>}
//       {error && <div className="error">{error}</div>}
//     </div>
//   );
// }
