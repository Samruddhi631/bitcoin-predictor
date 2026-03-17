// src/main.jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { wakeServer } from './services/api'

// Wake Render server the moment page loads
// This gives server ~30 seconds to warm up
// before user clicks anything
wakeServer()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)