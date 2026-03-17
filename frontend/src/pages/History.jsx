// src/pages/History.jsx
import { useState, useEffect } from 'react'
import { getHistory } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function History() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [days,    setDays]    = useState(30)

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const res = await getHistory(days)
        setData(res)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [days])

  const fmt = (n) => n && n !== 'pending'
    ? `$${Number(n).toLocaleString('en-US',
        { minimumFractionDigits: 2 })}`
    : '—'

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto',
                  padding: '24px 16px' }}>

      <div style={{
        display:        'flex',
        justifyContent: 'space-between',
        alignItems:     'center',
        marginBottom:   '24px',
      }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700' }}>
            Prediction History
          </h1>
          <p style={{ color: '#8b949e', fontSize: '13px',
                      marginTop: '4px' }}>
            Track accuracy of past predictions
          </p>
        </div>

        <select
          value={days}
          onChange={e => setDays(Number(e.target.value))}
          style={{
            background:   '#161b22',
            border:       '1px solid #30363d',
            borderRadius: '8px',
            color:        '#e6edf3',
            padding:      '8px 12px',
            fontSize:     '13px',
            cursor:       'pointer',
          }}
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Stats row */}
      {data?.stats && Object.keys(data.stats).length > 0 && (
        <div style={{
          display:             'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap:                 '16px',
          marginBottom:        '24px',
        }}>
          {[
            { label: 'Predictions Verified',
              value: data.stats.total_verified },
            { label: 'Direction Accuracy',
              value: `${data.stats.direction_acc}%`,
              color: data.stats.direction_acc >= 54
                       ? '#3fb950' : '#d29922' },
            { label: 'Avg Price Error',
              value: `$${data.stats.avg_error_usd?.toLocaleString()}` },
            { label: 'Avg % Error',
              value: `${data.stats.avg_error_pct}%` },
          ].map(s => (
            <div key={s.label} style={{
              background:   '#161b22',
              border:       '1px solid #30363d',
              borderRadius: '12px',
              padding:      '16px',
            }}>
              <div style={{
                fontSize:      '11px',
                color:         '#8b949e',
                textTransform: 'uppercase',
                marginBottom:  '8px',
              }}>
                {s.label}
              </div>
              <div style={{
                fontSize:   '24px',
                fontWeight: '700',
                color:      s.color || '#e6edf3',
              }}>
                {s.value}
              </div>
            </div>
          ))}
        </div>
      )}

      {loading ? <LoadingSpinner /> : (
        <div style={{
          background:   '#161b22',
          border:       '1px solid #30363d',
          borderRadius: '12px',
          overflow:     'hidden',
        }}>
          <table style={{
            width:           '100%',
            borderCollapse:  'collapse',
            fontSize:        '13px',
          }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #30363d' }}>
                {['Date','Price','Predicted','Direction',
                  'Confidence','Actual','Error','Correct?'
                ].map(h => (
                  <th key={h} style={{
                    padding:   '12px 16px',
                    textAlign: 'left',
                    color:     '#8b949e',
                    fontWeight:'500',
                  }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data?.predictions?.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{
                    padding:   '40px',
                    textAlign: 'center',
                    color:     '#8b949e',
                  }}>
                    No predictions yet — check back tomorrow!
                  </td>
                </tr>
              ) : (
                [...(data?.predictions || [])].reverse()
                  .map((p, i) => (
                  <tr key={i} style={{
                    borderBottom: '1px solid #21262d',
                    background:   i % 2 === 0
                                    ? 'transparent'
                                    : '#0d1117',
                  }}>
                    <td style={{ padding: '10px 16px' }}>
                      {p.date}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      {fmt(p.current_price)}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      {fmt(p.pred_tomorrow)}
                    </td>
                    <td style={{
                      padding: '10px 16px',
                      color:   p.direction?.includes('UP')
                                 ? '#3fb950' : '#f85149',
                    }}>
                      {p.direction}
                    </td>
                    <td style={{ padding: '10px 16px',
                                 color: '#8b949e' }}>
                      {p.confidence}%
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      {fmt(p.actual_price)}
                    </td>
                    <td style={{ padding: '10px 16px',
                                 color: '#8b949e' }}>
                      {p.error_usd !== 'pending' && p.error_usd
                        ? `$${Number(p.error_usd).toLocaleString()}`
                        : '—'}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      {p.direction_correct === 'pending' ||
                       p.direction_correct === null
                        ? <span style={{ color: '#8b949e' }}>—</span>
                        : p.direction_correct == 1
                          ? <span style={{ color: '#3fb950' }}>✅</span>
                          : <span style={{ color: '#f85149' }}>❌</span>
                      }
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}