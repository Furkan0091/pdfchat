import React from 'react';

const formatTime = (date) =>
  new Date(date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`msg ${isUser ? 'user' : 'assistant'}`}>
      <div className="msg-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div>
        <div className="msg-bubble">
          {message.content.split('\n').map((line, i) => (
            <span key={i}>{line}{i < message.content.split('\n').length - 1 && <br />}</span>
          ))}
        </div>
        <div className="msg-time">{formatTime(message.timestamp)}</div>
      </div>
    </div>
  );
}
