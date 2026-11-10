'use client';

import React, { useState } from 'react';

interface Citation {
  doc_id?: string;
  source?: string;
  score?: number;
  snippet: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Citation[];
  model?: string;
}

export default function GenAIChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I am your AWS Enterprise GenAI Assistant powered by Amazon Bedrock and OpenSearch Serverless. How can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input;
    setInput('');
    const newHistory = [...messages, { role: 'user' as const, content: userText }];
    setMessages(newHistory);
    setLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userText,
          history: messages.slice(-4),
          top_k: 4,
          use_hybrid: true
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setMessages([...newHistory, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        model: data.model
      }]);
    } catch (err: any) {
      setMessages([...newHistory, {
        role: 'assistant',
        content: `Error connecting to GenAI Backend: ${err.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: '900px', margin: '0 auto', padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <header style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '16px', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#0f172a' }}>
          ☁️ AWS Enterprise GenAI Assistant
        </h1>
        <p style={{ color: '#64748b', fontSize: '14px' }}>
          Amazon Bedrock (Claude 3.5 Sonnet) • OpenSearch Serverless • EKS • S3 Ingestion
        </p>
      </header>

      <div style={{ minHeight: '450px', maxHeight: '600px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', padding: '16px', background: '#f8fafc', borderRadius: '8px' }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{
            alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '80%',
            background: m.role === 'user' ? '#2563eb' : '#ffffff',
            color: m.role === 'user' ? '#ffffff' : '#1e293b',
            padding: '12px 16px',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <p style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{m.content}</p>

            {m.sources && m.sources.length > 0 && (
              <div style={{ marginTop: '12px', paddingTop: '8px', borderTop: '1px solid #e2e8f0', fontSize: '12px', color: '#475569' }}>
                <strong>Citations & Evidence:</strong>
                <ul style={{ paddingLeft: '16px', marginTop: '4px' }}>
                  {m.sources.map((s, sIdx) => (
                    <li key={sIdx}>
                      <span>{s.doc_id || s.source} (score: {s.score?.toFixed(3)})</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', color: '#64748b', fontStyle: 'italic' }}>
            Retrieving context from OpenSearch & invoking Bedrock...
          </div>
        )}
      </div>

      <form onSubmit={handleSend} style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your enterprise documents..."
          style={{ flex: 1, padding: '12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '15px' }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ background: '#2563eb', color: '#fff', padding: '0 24px', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </form>
    </main>
  );
}
