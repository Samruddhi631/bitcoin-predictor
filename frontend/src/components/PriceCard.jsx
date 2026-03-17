// src/components/PriceCard.jsx
export default function PriceCard({
  label, value, sub, subColor, highlight = false
}) {
  return (
    <div style={{
      background:   '#161b22',
      border:       `1px solid ${highlight
                      ? '#f7931a33'
                      : '#30363d'}`,
      borderRadius: '12px',
      padding:      '20px',
    }}>
      <div style={{
        fontSize:      '11px',
        color:         '#8b949e',
        textTransform: 'uppercase',
        letterSpacing: '0.8px',
        marginBottom:  '8px',
      }}>
        {label}
      </div>
      <div style={{
        fontSize:   '26px',
        fontWeight: '700',
        color:      highlight ? '#f7931a' : '#e6edf3',
      }}>
        {value}
      </div>
      {sub && (
        <div style={{
          fontSize:   '13px',
          color:      subColor || '#8b949e',
          marginTop:  '4px',
        }}>
          {sub}
        </div>
      )}
    </div>
  )
}