import { useState } from 'react';

interface ResponseMessage {
  role: string;
  content: string;
}

export default function Chat() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ResponseMessage[]>([]);

  async function sendQuery(e: React.FormEvent) {
    e.preventDefault();
    if (!query) return;

    const backend = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    try {
      const res = await fetch(`${backend}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (Array.isArray(data.responses)) {
        setMessages(data.responses.map((content: string) => ({ role: 'agent', content })));
      }
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="container">
      <form onSubmit={sendQuery}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something"
          style={{ width: '80%' }}
        />
        <button type="submit">Send</button>
      </form>
      <div className="messages">
        {messages.map((m, idx) => (
          <div key={idx} className="message">
            {m.content}
          </div>
        ))}
      </div>
    </div>
  );
}
