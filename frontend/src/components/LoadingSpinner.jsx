// src/components/LoadingSpinner.jsx
export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div style={{
      display:        'flex',
      flexDirection:  'column',
      alignItems:     'center',
      justifyContent: 'center',
      padding:        '80px 20px',
      gap:            '16px',
    }}>
      <div style={{
        width:        '40px',
        height:       '40px',
        border:       '3px solid #30363d',
        borderTop:    '3px solid #f7931a',
        borderRadius: '50%',
        animation:    'spin 1s linear infinite',
      }}/>
      <p style={{ color: '#8b949e', fontSize: '14px' }}>
        {message}
      </p>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}