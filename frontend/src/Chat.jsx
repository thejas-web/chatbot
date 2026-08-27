import { useState, useRef, useEffect } from "react";
import "./App.css";

function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const sessionIdRef = useRef(sessionStorage.getItem("webenza_session_id") || null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const autosize = (el) => {
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  const sendMessage = async (overrideText) => {
    const text = (overrideText ?? message).trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setMessage("");
    setLoading(true);
    requestAnimationFrame(() => autosize(textareaRef.current));

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text, session_id: sessionIdRef.current }),
      });

      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

      const data = await response.json();

      if (data.session_id) {
        sessionIdRef.current = data.session_id;
        sessionStorage.setItem("webenza_session_id", data.session_id);
      }

      // Optional: if your FastAPI endpoint returns a `sources` array
      // (e.g. [{ title, source }]), it renders as citation chips below
      // the answer. Safe to ignore if your backend doesn't send this yet.
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || "No answer returned.",
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Couldn't reach the backend. Check that the API is running on port 8000.",
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestions = [
    "Who are Webenza's clients?",
    "Where is Webenza located?",
    "What services does Webenza offer?",
  ];

  return (
    <div className="app">
      <div className="chat-container">
        <header className="chat-header">
          <div className="brand-mark">W</div>
          <div className="header-text">
            <h1>Webenza Assistant</h1>
            <p>Answers grounded in Webenza's own site content</p>
          </div>
        </header>

        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome">
              <h2>Ask about Webenza</h2>
              <p>Every answer is pulled from real pages on webenza.com — services, case studies, careers, and more.</p>
              <div className="suggestions">
                <span className="suggestions-label">Try asking</span>
                <div className="suggestions-row">
                  {suggestions.map((s) => (
                    <button key={s} onClick={() => sendMessage(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role}`}>
              <div className={`message ${msg.isError ? "error" : ""}`}>
                {msg.content}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    {msg.sources.map((src, i) => (
                      <a
                        key={i}
                        className="source-chip"
                        href={src.source}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {src.title || src.source}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row assistant">
              <div className="message thinking">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              autosize(e.target);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about Webenza…"
            rows="1"
          />
          <button
            className="send-btn"
            onClick={() => sendMessage()}
            disabled={loading || !message.trim()}
            aria-label="Send message"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path
                d="M4 12L20 4L14 20L11 13L4 12Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;