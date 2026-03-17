// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar     from './components/Navbar'
import Dashboard  from './pages/Dashboard'
import History    from './pages/History'
import About      from './pages/About'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"        element={<Dashboard />} />
        <Route path="/history" element={<History />}   />
        <Route path="/about"   element={<About />}     />
      </Routes>
    </BrowserRouter>
  )
}