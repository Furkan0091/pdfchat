import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import PDFUploader from './components/PDFUploader';
import ChatMessage from './components/ChatMessage';
import './index.css';

const SUGGESTED_QUESTIONS = [
  'Summarize this document',
  'What are the main points?',
  'What conclusions does it reach?',
  'List the key topics covered',
];

export default function App() {
  const [pdfInfo, setPdfInfo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef();
  const inputRef = useRef();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleUpload = (data) => {
    setPdfInfo(data);
    setMessages([
      {
        role: 'assistant',
        content: `I've read **${data.filename}** (${data.pages} page${data.pages !== 1 ? 's' : ''}, ~${data.wordCount.toLocaleString()} words). Ask me anything about it!`,
        timestamp: new Date(),
      },
    ]);
    setError('');
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleReset = () => {
    setPdfInfo(null);
    setMessages([]);
    setInput('');
    setError('');
  };

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg || loading || !pdfInfo) return;

    const userMsg = { role: 'user', content: msg, timestamp: new Date() };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);
    setError('');

    try {
      // Build history excluding the initial assistant greeting
      const history = updatedMessages.slice(1).map(m => ({
        role: m.role,
        content: m.content,
      }));

      const res = await axios.post('/api/chat', {
        fileId: pdfInfo.fileId,
        message: msg,
        history: history.slice(0, -1), // exclude the message we just sent
      });

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.reply,
        timestamp: new Date(),
      }]);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to get a response. Please try again.');
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-logo">
          <div className="navbar-logo-icon">📄</div>
          PDFChat
        </div>
        <span className="navbar-badge">Python · FastAPI · Groq AI</span>
      </nav>

      <div className="main">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-section">
            <div className="sidebar-label">Document</div>
            {!pdfInfo ? (
              <PDFUploader onUpload={handleUpload} />
            ) : (
              <div className="pdf-card">
                <div className="pdf-card-top">
                  <span className="pdf-icon">📄</span>
                  <span className="pdf-name">{pdfInfo.filename}</span>
                </div>
                <div className="pdf-meta">
                  <span className="pdf-meta-tag">{pdfInfo.pages} pages</span>
                  <span className="pdf-meta-tag">~{pdfInfo.wordCount?.toLocaleString()} words</span>
                </div>
                <span className="pdf-change" onClick={handleReset}>↩ Upload different PDF</span>
              </div>
            )}
          </div>

          {pdfInfo && (
            <div className="sidebar-section">
              <div className="sidebar-label">Suggested questions</div>
              <div className="tips-list">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <div key={q} className="tip-item" onClick={() => sendMessage(q)}>
                    <span className="tip-arrow">↗</span>
                    {q}
                  </div>
                ))}
              </div>
            </div>
          )}

          {messages.length > 1 && (
            <div className="sidebar-section">
              <button className="btn btn-ghost" style={{ width: '100%', justifyContent: 'center' }} onClick={() => setMessages(messages.slice(0, 1))}>
                🗑 Clear chat
              </button>
            </div>
          )}
        </aside>

        {/* Chat area */}
        <div className="chat-area">
          {!pdfInfo ? (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <div className="empty-title">Upload a PDF to get started</div>
              <div className="empty-sub">Upload any PDF document and ask questions about its content. Powered by Google Gemini AI.</div>
            </div>
          ) : (
            <>
              {/* Chat toolbar */}
              <div className="chat-toolbar">
                <div className="chat-filename">
                  Chatting about: <span>{pdfInfo.filename}</span>
                </div>
                <span style={{ fontSize: '12px', color: 'var(--muted)' }}>{messages.length - 1} message{messages.length !== 2 ? 's' : ''}</span>
              </div>

              {/* Messages */}
              <div className="messages">
                {error && <div className="error-bar">{error}</div>}

                {messages.map((msg, i) => (
                  <ChatMessage key={i} message={msg} />
                ))}

                {loading && (
                  <div className="msg assistant">
                    <div className="msg-avatar">🤖</div>
                    <div className="msg-bubble">
                      <div className="typing">
                        <span /><span /><span />
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="input-area">
                <div className="input-row">
                  <textarea
                    ref={inputRef}
                    className="input-box"
                    placeholder="Ask anything about your PDF..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={loading}
                    rows={1}
                  />
                  <button
                    className="send-btn"
                    onClick={() => sendMessage()}
                    disabled={loading || !input.trim()}
                  >
                    ➤
                  </button>
                </div>
                <div className="input-hint">Enter to send · Shift+Enter for new line</div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
