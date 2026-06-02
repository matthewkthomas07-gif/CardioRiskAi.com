import { FormEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  ChatResponse,
  checkHealth,
  fetchWelcome,
  sendChatMessage,
} from "../lib/api";

type Message = {
  id: string;
  role: "bot" | "user";
  text: string;
  prediction?: ChatResponse["prediction"];
};

const QUICK = ["start", "help", "restart"];

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [online, setOnline] = useState<boolean | null>(null);
  const [progress, setProgress] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkHealth().then(setOnline);
    fetchWelcome()
      .then((data) => {
        setSessionId(data.session_id);
        setMessages([
          { id: "welcome", role: "bot", text: data.reply },
        ]);
      })
      .catch(() => {
        setOnline(false);
        setMessages([
          {
            id: "err",
            role: "bot",
            text: "I can't reach the server. Start the API with **RUN_API.bat** or deploy the backend, then refresh.",
          },
        ]);
      });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const pushBot = (data: ChatResponse) => {
    setSessionId(data.session_id);
    const count = Object.keys(data.collected).length;
    setProgress(Math.round((count / 13) * 100));
    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: "bot",
        text: data.reply,
        prediction: data.prediction,
      },
    ]);
  };

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", text: trimmed },
    ]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage(trimmed, sessionId);
      pushBot(data);
      setOnline(true);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "bot",
          text: "Sorry — the connection failed. Check that the API is running and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    send(input);
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-left">
          <span className="pulse" aria-hidden />
          <div>
            <strong>CardioRisk AI Assistant</strong>
            <span className="chat-sub">
              {online === null
                ? "Connecting…"
                : online
                  ? "Model online"
                  : "Model offline"}
            </span>
          </div>
        </div>
        <div className="progress-wrap" title="Questions answered">
          <div className="progress-bar" style={{ width: `${progress}%` }} />
          <span>{progress}%</span>
        </div>
      </div>

      <div className="chat-messages" role="log" aria-live="polite">
        {messages.map((m) => (
          <div key={m.id} className={`bubble ${m.role}`}>
            <ReactMarkdown>{m.text}</ReactMarkdown>
            {m.prediction && (
              <div className="risk-card">
                <span className="risk-value">
                  {m.prediction.risk_percentage}%
                </span>
                <span className="risk-label">estimated cardiovascular risk</span>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="bubble bot typing">
            <span />
            <span />
            <span />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="quick-row">
        {QUICK.map((q) => (
          <button
            key={q}
            type="button"
            className="quick-btn"
            onClick={() => send(q)}
            disabled={loading}
          >
            {q}
          </button>
        ))}
      </div>

      <form className="chat-input-row" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your answer or 'start'…"
          disabled={loading}
          aria-label="Message"
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
