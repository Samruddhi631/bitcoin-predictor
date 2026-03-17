// src/services/api.js
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ||
                 'http://localhost:5000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 180000,  // 3 minutes max
})

// Wake server on app load
export const wakeServer = async () => {
  try {
    await api.get('/api/warmup', { timeout: 30000 })
    console.log('✅ Server warm')
  } catch (e) {
    console.log('⏳ Server waking...')
  }
}

export const getPrediction = async () => {
  const res = await api.get('/api/predict')
  return res.data
}

export const getHistory = async (days = 30) => {
  const res = await api.get(`/api/history?days=${days}`)
  return res.data
}

export const getMetrics = async () => {
  const res = await api.get('/api/metrics')
  return res.data
}

export const getHealth = async () => {
  const res = await api.get('/api/health')
  return res.data
}