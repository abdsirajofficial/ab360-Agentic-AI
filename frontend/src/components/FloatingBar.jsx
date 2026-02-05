import { useState, useRef, useEffect } from 'react'
import '../styles/FloatingBar.css'

function FloatingBar({ onToggle, isExpanded }) {
  const [position, setPosition] = useState({ x: window.innerWidth / 2 - 200, y: 20 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const barRef = useRef(null)

  const handleMouseDown = (e) => {
    if (e.target.closest('.bar-actions')) return
    
    setIsDragging(true)
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    })
  }

  const handleMouseMove = (e) => {
    if (!isDragging) return
    
    const newX = Math.max(0, Math.min(window.innerWidth - 400, e.clientX - dragOffset.x))
    const newY = Math.max(0, Math.min(window.innerHeight - 60, e.clientY - dragOffset.y))
    
    setPosition({ x: newX, y: newY })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, dragOffset])

  return (
    <div
      ref={barRef}
      className={`floating-bar ${isDragging ? 'dragging' : ''}`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`
      }}
      onMouseDown={handleMouseDown}
    >
      <div className="bar-content">
        <div className="bar-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="#2563EB" strokeWidth="2"/>
            <path d="M8 12h8M12 8v8" stroke="#2563EB" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span className="bar-title">ab360</span>
        </div>
        
        <div className="bar-actions">
          <button 
            className="bar-button"
            onClick={onToggle}
            title={isExpanded ? "Minimize" : "Expand"}
          >
            {isExpanded ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 9l-7 7-7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M5 15l7-7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </button>
        </div>
      </div>
      
      <div className="drag-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  )
}

export default FloatingBar
