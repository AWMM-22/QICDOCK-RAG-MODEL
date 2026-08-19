import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/chat'

const markdownToHtml = (text) => {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
    .replace(/\|/g, ' | ')
}

const SAMPLE_QUERIES = [
  'What is your refund policy?',
  'What is Mahindra refund policy?',
  'What is your shipping time?',
  'List all QICDOCK products',
  'What is Toyota Taisor charger price?',
  'What is your contact information?',
  'What is your warranty?',
  'What is the brand story?',
]

function App() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [intent, setIntent] = useState('')
  const [sources, setSources] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [showSamples, setShowSamples] = useState(true)
  const [showSources, setShowSources] = useState(false)
  const messagesEndRef = useRef(null)
  const chatAreaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    chatAreaRef.current?.scrollTo({ top: chatAreaRef.current.scrollHeight, behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [history, answer])

  const setQueryText = (text) => {
    setQuery(text)
    setShowSamples(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    const userMessage = query
    setQuery('')
    setShowSamples(false)
    setLoading(true)
    setError('')

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, session_id: sessionId })
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Request failed')
      }

      setAnswer(data.answer)
      setIntent(data.intent)
      setSources(data.sources)
      setSessionId(data.session_id)
      setHistory(prev => [...prev, { role: 'user', content: userMessage }, { role: 'assistant', content: data.answer }])
    } catch (err) {
      setError(err.message)
      setAnswer('')
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setQuery('')
    setAnswer('')
    setIntent('')
    setSources([])
    setSessionId(null)
    setError('')
    setHistory([])
    setShowSamples(true)
    setShowSources(false)
  }

  const toggleSources = () => setShowSources(!showSources)

  return (
    <div className="app">
      <header>
        <div className="header-content">
          <h1>QICDOCK</h1>
          <p>RAG Chatbot</p>
        </div>
        <button className="btn-clear" onClick={clearChat} title="New chat">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 3h18v18H3z"></path>
            <path d="M3 9h18"></path>
            <path d="M9 3v18"></path>
          </svg>
        </button>
      </header>

      <div className="chat-container" ref={chatAreaRef}>
        {showSamples && history.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <h2>How can I help you?</h2>
            <p>Ask me about QICDOCK products, policies, shipping, warranty, and more.</p>
            <div className="sample-queries">
              {SAMPLE_QUERIES.map((q, i) => (
                <button key={i} className="sample-btn" onClick={() => setQueryText(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-history">
            {history.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                <div className="message-bubble">
                  <div className="message-content" dangerouslySetInnerHTML={{ __html: markdownToHtml(msg.content) }} />
                </div>
              </div>
            ))}
            {answer && history.length === 0 && (
              <div className="message assistant">
                <div className="message-bubble">
                  <div className="message-content answer" dangerouslySetInnerHTML={{ __html: markdownToHtml(answer) }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {error && <div className="error-banner">{error}</div>}
      </div>

      {(intent || sources.length > 0) && (
        <div className="meta-bar" onClick={toggleSources}>
          <div className="meta-items">
            {intent && <span><strong>Intent:</strong> {intent}</span>}
            {sessionId && <span><strong>Session:</strong> {sessionId.slice(0, 8)}...</span>}
            {sources.length > 0 && <span><strong>Sources:</strong> {sources.length}</span>}
          </div>
          {sources.length > 0 && (
            <span className="meta-toggle">
              {showSources ? 'Hide Sources' : 'View Sources'}
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 9l6 6 6-6"></path>
              </svg>
            </span>
          )}
        </div>
      )}

      {showSources && sources.length > 0 && (
        <div className="sources-panel">
          <ul>
            {sources.map((src, i) => (
              <li key={i}>
                <strong>{src.type === 'product' ? src.product_name : src.filename}</strong>
                <pre>{JSON.stringify(src.metadata, null, 2)}</pre>
              </li>
            ))}
          </ul>
        </div>
      )}

      <form onSubmit={handleSubmit} className="input-area">
        <div className="input-wrapper">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={history.length === 0 ? "Ask about products, policies, shipping..." : "Type a message..."}
            rows={1}
            disabled={loading}
            ref={(el) => { if (el) el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 120) + 'px'; }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
          />
        </div>
        <div className="input-actions">
          <button type="submit" className="btn-send" disabled={loading || !query.trim()} aria-label="Send message">
            {loading ? (
              <span className="spinner"></span>
            ) : (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M22 2L11 13"></path>
                <path d="M22 2l-7 20-4-9-9-4 20-7z"></path>
              </svg>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default App