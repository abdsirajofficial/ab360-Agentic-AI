import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import '../styles/AssistantWidget.css'

const API_URL = 'http://localhost:8000'

function AssistantWidget() {
  const [isExpanded, setIsExpanded] = useState(false)
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m ab360, your intelligent AI assistant. I can help you with planning, learning, notes, and more. What would you like to do today?'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const messagesEndRef = useRef(null)
  
  // Draggable state for chat window
  const [chatPosition, setChatPosition] = useState({ x: 0, y: 0 })
  const [isChatDragging, setIsChatDragging] = useState(false)
  const [chatDragStart, setChatDragStart] = useState({ x: 0, y: 0 })
  const chatRef = useRef(null)
  
  // Resizable chat height
  const [chatHeight, setChatHeight] = useState(600)
  const [isResizing, setIsResizing] = useState(false)
  const [resizeStartY, setResizeStartY] = useState(0)
  const [resizeStartHeight, setResizeStartHeight] = useState(600)

  // Draggable state for trigger button
  const [triggerPosition, setTriggerPosition] = useState({ x: 0, y: 0 })
  const [isTriggerDragging, setIsTriggerDragging] = useState(false)
  const [triggerDragStart, setTriggerDragStart] = useState({ x: 0, y: 0 })
  const [triggerMouseDownPos, setTriggerMouseDownPos] = useState({ x: 0, y: 0 })
  const triggerRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const toggleExpand = () => {
    setIsExpanded(!isExpanded)
    if (!isExpanded) {
      setChatPosition({ x: 0, y: 0 }) // Reset chat position when opening
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    
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

  // Chat window dragging handlers
  const handleChatMouseDown = (e) => {
    if (e.target.closest('.chat-header') && !e.target.closest('.close-btn')) {
      setIsChatDragging(true)
      setChatDragStart({
        x: e.clientX - chatPosition.x,
        y: e.clientY - chatPosition.y
      })
    }
  }

  const handleChatMouseMove = (e) => {
    if (isChatDragging) {
      setChatPosition({
        x: e.clientX - chatDragStart.x,
        y: e.clientY - chatDragStart.y
      })
    }
  }

  const handleChatMouseUp = () => {
    setIsChatDragging(false)
  }

  // Resize handlers
  const handleResizeMouseDown = (e) => {
    setIsResizing(true)
    setResizeStartY(e.clientY)
    setResizeStartHeight(chatHeight)
    e.preventDefault()
    e.stopPropagation()
  }

  const handleResizeMouseMove = (e) => {
    if (isResizing) {
      const deltaY = resizeStartY - e.clientY // Inverted because growing upward
      const newHeight = Math.max(300, Math.min(900, resizeStartHeight + deltaY))
      setChatHeight(newHeight)
    }
  }

  const handleResizeMouseUp = () => {
    setIsResizing(false)
  }

  // Trigger button dragging handlers
  const handleTriggerMouseDown = (e) => {
    // Record initial mouse position
    setTriggerMouseDownPos({ x: e.clientX, y: e.clientY })
    setTriggerDragStart({
      x: e.clientX - triggerPosition.x,
      y: e.clientY - triggerPosition.y
    })
    e.preventDefault() // Prevent text selection
  }

  const handleTriggerMouseMove = (e) => {
    // Check if mouse moved more than 5px since mousedown
    const deltaX = Math.abs(e.clientX - triggerMouseDownPos.x)
    const deltaY = Math.abs(e.clientY - triggerMouseDownPos.y)
    
    if (deltaX > 5 || deltaY > 5) {
      setIsTriggerDragging(true)
      setTriggerPosition({
        x: e.clientX - triggerDragStart.x,
        y: e.clientY - triggerDragStart.y
      })
    }
  }

  const handleTriggerMouseUp = (e) => {
    // Calculate distance moved since mousedown
    const deltaX = Math.abs(e.clientX - triggerMouseDownPos.x)
    const deltaY = Math.abs(e.clientY - triggerMouseDownPos.y)
    const dragDistance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
    
    // If moved less than 5px, treat as click
    if (dragDistance < 5 && !isTriggerDragging) {
      toggleExpand()
    }
    
    setIsTriggerDragging(false)
  }

  useEffect(() => {
    if (isChatDragging) {
      document.addEventListener('mousemove', handleChatMouseMove)
      document.addEventListener('mouseup', handleChatMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleChatMouseMove)
        document.removeEventListener('mouseup', handleChatMouseUp)
      }
    }
  }, [isChatDragging, chatDragStart])

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleResizeMouseMove)
      document.addEventListener('mouseup', handleResizeMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleResizeMouseMove)
        document.removeEventListener('mouseup', handleResizeMouseUp)
      }
    }
  }, [isResizing, resizeStartY, resizeStartHeight])

  useEffect(() => {
    // Always listen for mouse events after mousedown
    const handleMove = (e) => handleTriggerMouseMove(e)
    const handleUp = (e) => handleTriggerMouseUp(e)
    
    if (triggerMouseDownPos.x !== 0 || triggerMouseDownPos.y !== 0) {
      document.addEventListener('mousemove', handleMove)
      document.addEventListener('mouseup', handleUp)
      return () => {
        document.removeEventListener('mousemove', handleMove)
        document.removeEventListener('mouseup', handleUp)
      }
    }
  }, [triggerMouseDownPos, isTriggerDragging, triggerDragStart, triggerPosition])

  return (
    <div className={`assistant-widget ${isExpanded ? 'expanded' : ''}`}>
      {/* Floating Button - Hidden when expanded, Draggable */}
      {!isExpanded && (
        <button 
          ref={triggerRef}
          className="assistant-trigger"
          onMouseDown={handleTriggerMouseDown}
          aria-label="Toggle AI Assistant"
          style={{
            transform: `translate(${triggerPosition.x}px, ${triggerPosition.y}px)`,
            cursor: isTriggerDragging ? 'grabbing' : 'grab'
          }}
        >
          <div className="trigger-content">
            <div className="ai-logo">
              <div className="logo-circle">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="pulse-rings">
                <span className="pulse-ring"></span>
                <span className="pulse-ring"></span>
              </div>
            </div>
            <div className="trigger-label">
              <span className="ai-name">ab360</span>
              <span className="ai-badge">AI</span>
            </div>
          </div>
        </button>
      )}

      {/* Chat Window - Draggable */}
      {isExpanded && (
        <div 
          ref={chatRef}
          className="chat-container"
          style={{
            transform: `translate(${chatPosition.x}px, ${chatPosition.y}px)`,
            height: `${chatHeight}px`,
            cursor: isChatDragging ? 'grabbing' : 'default'
          }}
        >
          {/* Resize Handle */}
          <div 
            className="resize-handle"
            onMouseDown={handleResizeMouseDown}
            title="Drag to resize"
          >
            <div className="resize-indicator"></div>
          </div>
          <div 
            className="chat-header"
            onMouseDown={handleChatMouseDown}
            style={{ cursor: 'grab' }}
          >
            <div className="header-left">
              <div className="header-logo">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="header-info">
                <h3>ab360 Assistant</h3>
                <span className="status">
                  <span className="status-dot"></span>
                  Online
                </span>
              </div>
            </div>
            <button className="close-btn" onClick={toggleExpand} aria-label="Close">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>
          </div>

          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`message message-${message.role}`}>
                <div className="message-avatar">
                  {message.role === 'user' ? (
                    <div className="avatar-user">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                  ) : (
                    <div className="avatar-ai">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                  )}
                </div>
                <div className="message-content">
                  <div className="message-text">
                    {message.role === 'assistant' ? (
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          table: ({node, ...props}) => <table className="markdown-table" {...props} />,
                          th: ({node, ...props}) => <th className="markdown-th" {...props} />,
                          td: ({node, ...props}) => <td className="markdown-td" {...props} />,
                          code: ({node, inline, ...props}) => 
                            inline ? <code className="markdown-code-inline" {...props} /> 
                                   : <code className="markdown-code-block" {...props} />,
                          h1: ({node, ...props}) => <h1 className="markdown-h1" {...props} />,
                          h2: ({node, ...props}) => <h2 className="markdown-h2" {...props} />,
                          h3: ({node, ...props}) => <h3 className="markdown-h3" {...props} />,
                          ul: ({node, ...props}) => <ul className="markdown-ul" {...props} />,
                          ol: ({node, ...props}) => <ol className="markdown-ol" {...props} />,
                          li: ({node, ...props}) => <li className="markdown-li" {...props} />,
                          blockquote: ({node, ...props}) => <blockquote className="markdown-blockquote" {...props} />,
                          hr: ({node, ...props}) => <hr className="markdown-hr" {...props} />,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    ) : (
                      message.content
                    )}
                  </div>
                  {message.intent && (
                    <div className="message-badges">
                      <span className="badge intent-badge">{message.intent}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message message-assistant">
                <div className="message-avatar">
                  <div className="avatar-ai">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                </div>
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

          <div className="chat-input-area">
            <div className="input-container">
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
                className="send-btn"
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                aria-label="Send message"
              >
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 8L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
            <div className="input-hint">
              Press <kbd>Enter</kbd> to send • <kbd>Shift + Enter</kbd> for new line
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AssistantWidget
