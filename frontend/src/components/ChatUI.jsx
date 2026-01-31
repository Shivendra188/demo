import { sendCommand } from "../services/api";

const handleSend = async () => {
  try {
    const res = await sendCommand(userInput);

    console.log(res.taskType);  // QUOTE | POLICY | REMINDER | CRM
    console.log(res.response);  // actual AI output

    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: res.response }
    ]);
  } catch (err) {
    setMessages((prev) => [
      ...prev,
      { role: "system", content: err.message }
    ]);
  }
};
