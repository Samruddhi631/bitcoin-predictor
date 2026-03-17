// src/components/FeatureChart.jsx
import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, Tooltip, Cell
} from 'recharts'

export default function FeatureChart({ importance }) {
  if (!importance) return null

  const data = Object.entries(importance)
    .slice(0, 10)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => a.value - b.value)

  const colors = data.map(d =>
    d.value > 0.05 ? '#f85149' :
    d.value > 0.02 ? '#f7931a' :
                     '#388bfd'
  )

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
        Feature Importance (XGBoost)
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout="vertical">
          <XAxis
            type="number"
            tick={{ fill: '#8b949e', fontSize: 11 }}
            stroke="#30363d"
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: '#8b949e', fontSize: 11 }}
            stroke="#30363d"
            width={110}
          />
          <Tooltip
            contentStyle={{
              background:   '#161b22',
              border:       '1px solid #30363d',
              borderRadius: '8px',
              color:        '#e6edf3',
            }}
            formatter={(val) => [val.toFixed(4), 'Importance']}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}