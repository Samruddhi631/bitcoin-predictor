// src/components/PriceChart.jsx
import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts'

export default function PriceChart({ history, predictions }) {
  if (!history || !history.dates) return null

  // Build chart data
  const actualData = history.dates.map((date, i) => ({
    date:   date.slice(5),   // show MM-DD only
    actual: history.prices[i],
  }))

  // Add forecast points
  const lastPrice = history.prices[history.prices.length - 1]
  const forecastData = [
    { date: 'Today',    forecast: lastPrice },
    { date: 'Tomorrow', forecast: predictions?.tomorrow?.price },
    { date: '+3 Days',  forecast: predictions?.['3day']?.price },
    { date: '+7 Days',  forecast: predictions?.['7day']?.price },
  ]

  const combined = [
    ...actualData,
    ...forecastData.slice(1),
  ]

  // Add forecast to last actual point for continuity
  combined[actualData.length - 1] = {
    ...combined[actualData.length - 1],
    forecast: lastPrice,
  }

  const fmt = (v) => v
    ? `$${Number(v).toLocaleString('en-US',
        { minimumFractionDigits: 0 })}`
    : ''

  return (
    <div style={{
      background:   '#161b22',
      border:       '1px solid #30363d',
      borderRadius: '12px',
      padding:      '20px',
    }}>
      <div style={{
        fontSize:     '14px',
        fontWeight:   '600',
        marginBottom: '16px',
      }}>
        BTC Price — Last 30 Days + Forecast
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={combined}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#21262d"
          />
          <XAxis
            dataKey="date"
            tick={{ fill: '#8b949e', fontSize: 11 }}
            interval={4}
            stroke="#30363d"
          />
          <YAxis
            tickFormatter={fmt}
            tick={{ fill: '#8b949e', fontSize: 11 }}
            stroke="#30363d"
            width={80}
          />
          <Tooltip
            contentStyle={{
              background:   '#161b22',
              border:       '1px solid #30363d',
              borderRadius: '8px',
              color:        '#e6edf3',
            }}
            formatter={(val) => [fmt(val)]}
          />
          <Legend
            wrapperStyle={{ color: '#8b949e', fontSize: 12 }}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#388bfd"
            strokeWidth={2}
            dot={false}
            name="Actual Price"
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#f7931a"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={{ fill: '#f7931a', r: 4 }}
            name="Forecast"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}