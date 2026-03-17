// src/components/Navbar.jsx
import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const { pathname } = useLocation()

  const links = [
    { to: '/',         label: 'Dashboard' },
    { to: '/history',  label: 'History'   },
    { to: '/about',    label: 'About'     },
  ]

  return (
    <nav style={{
      background:   '#161b22',
      borderBottom: '1px solid #30363d',
      padding:      '0 24px',
      display:      'flex',
      alignItems:   'center',
      gap:          '8px',
      height:       '60px',
      position:     'sticky',
      top:          0,
      zIndex:       100,
    }}>
      {/* Logo */}
      <Link to="/" style={{
        fontSize:   '20px',
        fontWeight: '700',
        color:      '#f7931a',
        marginRight:'24px',
      }}>
        ₿ Bitcoin Predictor
      </Link>

      {/* Links */}
      {links.map(link => (
        <Link
          key={link.to}
          to={link.to}
          style={{
            padding:      '6px 14px',
            borderRadius: '8px',
            fontSize:     '14px',
            color:        pathname === link.to
                            ? '#e6edf3'
                            : '#8b949e',
            background:   pathname === link.to
                            ? '#21262d'
                            : 'transparent',
            transition:   'all 0.15s',
          }}
        >
          {link.label}
        </Link>
      ))}

      {/* Live badge */}
      <div style={{ marginLeft: 'auto' }}>
        <span style={{
          background:   '#1a3a1a',
          color:        '#3fb950',
          border:       '1px solid #3fb950',
          borderRadius: '20px',
          padding:      '3px 12px',
          fontSize:     '12px',
        }}>
          ● LIVE
        </span>
      </div>
    </nav>
  )
}