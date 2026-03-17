// src/components/DirectionCard.jsx
export default function DirectionCard({ direction, confidence, tier }) {
  const isUp    = direction === 'UP'
  const color   = isUp ? '#3fb950' : '#f85149'
  const icon    = isUp ? '📈' : '📉'
  const label   = isUp ? 'BULLISH' : 'BEARISH'

  const tierColor = tier === 'HIGH'   ? '#3fb950' :
                    tier === 'MEDIUM' ? '#d29922' :
                                        '#8b949e'

  return (
    <div style={{
      background:   '#161b22',
      border:       '1px solid #30363d',
      borderRadius: '12px',
      padding:      '24px',
      textAlign:    'center',
    }}>
      <div style={{
        fontSize:      '11px',
        color:         '#8b949e',
        textTransform: 'uppercase',
        letterSpacing: '0.8px',
        marginBottom:  '12px',
      }}>
        Direction Signal
      </div>

      <div style={{ fontSize: '52px', marginBottom: '8px' }}>
        {icon}
      </div>

      <div style={{
        fontSize:     '26px',
        fontWeight:   '700',
        color:        color,
        marginBottom: '6px',
      }}>
        {label}
      </div>

      <div style={{ fontSize: '13px', color: '#8b949e' }}>
        Confidence: {confidence}%
      </div>

      {/* Confidence bar */}
      <div style={{
        background:   '#21262d',
        borderRadius: '8px',
        height:       '8px',
        margin:       '12px 0 8px',
        overflow:     'hidden',
      }}>
        <div style={{
          height:           '100%',
          width:            `${confidence}%`,
          borderRadius:     '8px',
          background:       'linear-gradient(90deg, #1f6feb, #388bfd)',
          transition:       'width 0.5s ease',
        }}/>
      </div>

      <div style={{ fontSize: '12px', color: tierColor }}>
        Signal strength: {tier}
      </div>
    </div>
  )
}