// src/pages/About.jsx
export default function About() {
  const sections = [
    {
      title: 'What is this?',
      content: `A machine learning system that predicts Bitcoin price direction
        and targets using XGBoost and Random Forest ensemble models,
        trained on 9 years of historical data (2017–2026).`
    },
    {
      title: 'How does it work?',
      content: `Every day the system fetches live BTC price, SP500, Fear & Greed
        index and builds 30+ technical features including RSI, MACD, Bollinger
        Bands, and Bitcoin Halving cycle position. The ensemble model then
        predicts tomorrow's price direction and 1/3/7 day price targets.`
    },
    {
      title: 'How accurate is it?',
      content: `Backtest direction accuracy: 54.3%. Walk-forward validation: 52.6%.
        At 62%+ confidence: 57.4%. The model performs best during trending markets
        and struggles during black swan events — which is true for all financial ML models.`
    },
    {
      title: 'What factors does it consider?',
      content: `Supply & Demand (Volume, RSI, MACD, Bollinger Bands),
        Market Sentiment (Fear & Greed Index, Google Trends),
        Macroeconomics (SP500 correlation),
        Bitcoin Halving Cycle (4th most important feature).`
    },
    {
      title: '⚠️ Disclaimer',
      content: `This is a research and educational project only. Nothing on this
        website constitutes financial advice. Never make investment decisions
        based solely on ML model predictions. Always do your own research.`
    },
  ]

  const stack = [
    { label: 'ML Models',   value: 'XGBoost + Random Forest' },
    { label: 'Validation',  value: 'Walk-Forward (30 windows)' },
    { label: 'Backend',     value: 'Python + Flask' },
    { label: 'Frontend',    value: 'React + Vite + Recharts' },
    { label: 'ML Training', value: 'Google Colab' },
    { label: 'API Host',    value: 'Render.com' },
    { label: 'Frontend',    value: 'Vercel' },
    { label: 'Automation',  value: 'GitHub Actions' },
    { label: 'Data',        value: 'Yahoo Finance + CoinGecko + Alternative.me' },
  ]

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto',
                  padding: '24px 16px' }}>
      <h1 style={{ fontSize: '24px', fontWeight: '700',
                   marginBottom: '8px' }}>
        About This Project
      </h1>
      <p style={{ color: '#8b949e', fontSize: '13px',
                  marginBottom: '32px' }}>
        Built with machine learning + full-stack development
      </p>

      {/* Sections */}
      {sections.map(s => (
        <div key={s.title} style={{
          background:   '#161b22',
          border:       '1px solid #30363d',
          borderRadius: '12px',
          padding:      '20px',
          marginBottom: '16px',
        }}>
          <h2 style={{ fontSize: '16px', fontWeight: '600',
                       marginBottom: '10px' }}>
            {s.title}
          </h2>
          <p style={{ color: '#8b949e', lineHeight: '1.7',
                      fontSize: '14px' }}>
            {s.content}
          </p>
        </div>
      ))}

      {/* Tech Stack */}
      <div style={{
        background:   '#161b22',
        border:       '1px solid #30363d',
        borderRadius: '12px',
        padding:      '20px',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: '600',
                     marginBottom: '16px' }}>
          Tech Stack
        </h2>
        <div style={{
          display:             'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap:                 '10px',
        }}>
          {stack.map(s => (
            <div key={s.label} style={{
              background:   '#21262d',
              borderRadius: '8px',
              padding:      '10px 14px',
              display:      'flex',
              justifyContent: 'space-between',
            }}>
              <span style={{ color: '#8b949e',
                             fontSize: '13px' }}>
                {s.label}
              </span>
              <span style={{ color: '#e6edf3',
                             fontSize: '13px',
                             fontWeight: '500' }}>
                {s.value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}