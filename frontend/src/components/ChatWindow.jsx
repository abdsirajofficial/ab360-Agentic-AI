import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import '../styles/ChatWindow.css'

const API_URL = 'http://localhost:8000'

function ChatWindow({ onClose }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m ab360, your personal AI assistant. I can help you with daily planning, learning, note-taking, and more. How can I assist you today?'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: userMessage,
        session_id: sessionId
      })

      if (!sessionId) {
        setSessionId(response.data.session_id)
      }

      // Add assistant response
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response.data.response,
          intent: response.data.intent,
          tool_calls: response.data.tool_calls
        }
      ])
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please make sure the backend is running on port 8000.',
          error: true
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h2>ab360 Assistant</h2>
        <button className="close-button" onClick={onClose}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message message-${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              {message.intent && (
                <div className="message-meta">
                  <span className="intent-badge">{message.intent}</span>
                </div>
              )}
              {message.tool_calls && message.tool_calls.length > 0 && (
                <div className="message-meta">
                  <span className="tool-badge">Tools: {message.tool_calls.join(', ')}</span>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message message-assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <div className="input-wrapper">
          <textarea
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            rows="1"
            disabled={isLoading}
          />
          <button
            className="send-button"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
        <div className="input-hint">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}

export default ChatWindow
