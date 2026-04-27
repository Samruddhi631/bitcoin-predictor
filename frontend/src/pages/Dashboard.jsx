// src/pages/Dashboard.jsx
import { useState, useEffect } from 'react'
import { getPrediction, getMetrics } from '../services/api'
import PriceCard      from '../components/PriceCard'
import PriceChart     from '../components/PriceChart'
import DirectionCard  from '../components/DirectionCard'
import FeatureChart   from '../components/FeatureChart'
import LoadingSpinner from '../components/LoadingSpinner'

const fmt = (n) =>
  `$${Number(n).toLocaleString('en-US',
    { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

const pctColor = (v) =>
  Number(v) >= 0 ? '#3fb950' : '#f85149'

const pctStr = (v) =>
  `${Number(v) >= 0 ? '+' : ''}${Number(v).toFixed(3)}%`

export default function Dashboard() {
  const [data,    setData]    = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const [pred, met] = await Promise.all([
          getPrediction(),
          getMetrics(),
        ])
        if (!pred.success) throw new Error(pred.error)
        setData(pred)
        setMetrics(met)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return (
    <LoadingSpinner message="Waking up server + fetching live BTC data... Please wait up to 90 seconds on first load" />
  )

  if (error) return (
    <div style={{
      textAlign: 'center', padding: '80px 20px',
      color: '#f85149'
    }}>
      <h2>⚠️ Failed to load prediction</h2>
      <p style={{ marginTop: '12px', color: '#8b949e' }}>
        {error}
      </p>
      <button
        onClick={() => window.location.reload()}
        style={{
          marginTop:    '20px',
          padding:      '10px 24px',
          background:   '#f7931a',
          border:       'none',
          borderRadius: '8px',
          color:        '#fff',
          cursor:       'pointer',
          fontSize:     '14px',
        }}
      >
        Retry
      </button>
    </div>
  )

  const { predictions, direction, market,
          price_history, current_price, date } = data

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto',
                  padding: '24px 16px' }}>

      {/* Page header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{
          fontSize: '24px', fontWeight: '700'
        }}>
          Bitcoin Price Predictor
        </h1>
        <p style={{ color: '#8b949e', fontSize: '13px',
                    marginTop: '4px' }}>
          ML model using XGBoost + Random Forest + Ensemble
          · Data as of {date}
        </p>
      </div>

      {/* Row 1: 3 stat cards */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap:                 '16px',
        marginBottom:        '16px',
      }}>
        <PriceCard
          label="Current BTC Price"
          value={fmt(current_price)}
          sub={`As of ${date}`}
          highlight
        />
        <PriceCard
          label="Tomorrow's Forecast"
          value={fmt(predictions.tomorrow.price)}
          sub={pctStr(predictions.tomorrow.return)}
          subColor={pctColor(predictions.tomorrow.return)}
        />
        <PriceCard
          label="Market Regime"
          value={market.regime === 'Bull' ? ' Bull'
               : market.regime === 'Bear' ? ' Bear'
               : ' Sideways'}
          sub={`Fear & Greed: ${market.fear_greed}/100`}
        />
      </div>

      {/* Row 2: 4 metric cards */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap:                 '16px',
        marginBottom:        '16px',
      }}>
        {[
          { label: 'Backtest Accuracy',
            value: '54.3%', color: '#3fb950' },
          { label: 'High Conf Accuracy',
            value: '57.4%', color: '#3fb950' },
          { label: 'Walk-Forward',
            value: '52.6%', color: '#d29922' },
          { label: 'Model Stability',
            value: '1.7% gap', color: '#3fb950' },
        ].map(m => (
          <div key={m.label} style={{
            background:   '#161b22',
            border:       '1px solid #30363d',
            borderRadius: '12px',
            padding:      '16px',
          }}>
            <div style={{
              fontSize:      '11px',
              color:         '#8b949e',
              textTransform: 'uppercase',
              letterSpacing: '0.8px',
              marginBottom:  '8px',
            }}>
              {m.label}
            </div>
            <div style={{
              fontSize:   '22px',
              fontWeight: '700',
              color:      m.color,
            }}>
              {m.value}
            </div>
          </div>
        ))}
      </div>

      {/* Row 3: Chart */}
      <div style={{ marginBottom: '16px' }}>
        <PriceChart
          history={price_history}
          predictions={predictions}
        />
      </div>

      {/* Row 4: Direction + Targets */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap:                 '16px',
        marginBottom:        '16px',
      }}>
        <DirectionCard
          direction={direction.signal}
          confidence={direction.confidence}
          tier={direction.tier}
        />

        {/* Price targets */}
        <div style={{
          background:   '#161b22',
          border:       '1px solid #30363d',
          borderRadius: '12px',
          padding:      '20px',
        }}>
          <div style={{
            fontSize:      '11px',
            color:         '#8b949e',
            textTransform: 'uppercase',
            letterSpacing: '0.8px',
            marginBottom:  '16px',
          }}>
            Price Targets
          </div>

          {[
            { label: 'Tomorrow',   key: 'tomorrow' },
            { label: '3-Day',      key: '3day'     },
            { label: '7-Day',      key: '7day'     },
          ].map(t => (
            <div key={t.key} style={{
              display:        'flex',
              justifyContent: 'space-between',
              alignItems:     'center',
              background:     '#21262d',
              borderRadius:   '8px',
              padding:        '12px 16px',
              marginBottom:   '8px',
            }}>
              <span style={{
                fontSize: '13px', color: '#8b949e'
              }}>
                {t.label}
              </span>
              <div style={{ textAlign: 'right' }}>
                <div style={{
                  fontSize:   '16px',
                  fontWeight: '700',
                  color:      pctColor(
                    predictions[t.key].return),
                }}>
                  {fmt(predictions[t.key].price)}
                </div>
                <div style={{
                  fontSize: '12px',
                  color:    pctColor(
                    predictions[t.key].return),
                }}>
                  {pctStr(predictions[t.key].return)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Row 5: Feature Importance + Model Info */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap:                 '16px',
        marginBottom:        '16px',
      }}>
        <FeatureChart
          importance={metrics?.feature_importance}
        />

        {/* Model details */}
        <div style={{
          background:   '#161b22',
          border:       '1px solid #30363d',
          borderRadius: '12px',
          padding:      '20px',
        }}>
          <div style={{
            fontSize:      '11px',
            color:         '#8b949e',
            textTransform: 'uppercase',
            letterSpacing: '0.8px',
            marginBottom:  '16px',
          }}>
            Model Details
          </div>

          <div style={{
            display:             'grid',
            gridTemplateColumns: '1fr 1fr',
            gap:                 '10px',
          }}>
            {[
              { label: 'Training Period',
                value: '2017–2026' },
              { label: 'Training Rows',
                value: '3,298' },
              { label: 'Features Used',
                value: metrics?.model_metrics
                              ?.features_count || '—' },
              { label: 'Models in Ensemble',
                value: '3' },
              { label: 'Halving Feature',
                value: '4th rank', color: '#3fb950' },
              { label: 'Walk-Forward',
                value: '30 windows' },
            ].map(m => (
              <div key={m.label} style={{
                background:   '#21262d',
                borderRadius: '8px',
                padding:      '12px',
              }}>
                <div style={{
                  fontSize: '11px', color: '#8b949e',
                  marginBottom: '4px',
                }}>
                  {m.label}
                </div>
                <div style={{
                  fontSize:   '16px',
                  fontWeight: '600',
                  color:      m.color || '#e6edf3',
                }}>
                  {m.value}
                </div>
              </div>
            ))}
          </div>

          <div style={{
            background:   '#1a1500',
            border:       '1px solid #d29922',
            borderRadius: '8px',
            padding:      '12px',
            marginTop:    '14px',
            fontSize:     '12px',
            color:        '#8b949e',
            lineHeight:   '1.6',
          }}>
            ⚠️ Research tool only. Not financial advice.
            Past performance does not guarantee future results.
          </div>
        </div>
      </div>
    </div>
  )
}