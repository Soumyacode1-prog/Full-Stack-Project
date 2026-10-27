import { useEffect, useState } from 'react'
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const number = (value) => value == null ? '—' : new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(value)
const timeLabel = (value) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

export default function App() {
  const [date, setDate] = useState('2026-10-26')
  const [cutoff, setCutoff] = useState('23:00')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadDashboard() {
    setLoading(true); setError('')
    try {
      const response = await fetch(`${API_URL}/api/dashboard?decision_date=${date}&cutoff=${cutoff}`)
      const body = await response.json()
      if (!response.ok) throw new Error(body.detail || 'Failed to fetch dashboard data')
      setData(body)
    } catch (requestError) { setData(null); setError(requestError.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { loadDashboard() }, [])

  return <main className="dashboard-shell">
    <header className="page-header"><div><p className="eyebrow">REint Energy Analytics</p><h1>Wind Forecast Dashboard</h1><p className="subtitle">Compare forecast values with actual wind generation.</p></div><span className="status-pill">● Live analysis</span></header>
    <section className="filter-card"><div className="field"><label htmlFor="date">Decision date</label><input id="date" type="date" value={date} onChange={(event) => setDate(event.target.value)} /></div><div className="field"><label htmlFor="cutoff">Forecast cutoff</label><input id="cutoff" type="time" value={cutoff} onChange={(event) => setCutoff(event.target.value)} /></div><button onClick={loadDashboard} disabled={loading}>{loading ? 'Loading…' : 'Run analysis'}</button></section>
    {error && <div className="alert">{error}</div>}
    {loading && <div className="empty-state">Loading dashboard…</div>}
    {data && !loading && <><section className="kpi-grid"><article><span>Actual generation</span><strong>{number(data.summary.actualGeneration)}</strong><small>MWh</small></article><article><span>Selected forecast</span><strong>{number(data.summary.forecastGeneration)}</strong><small>MWh</small></article><article><span>Absolute error</span><strong>{number(data.summary.absoluteError)}</strong><small>MWh</small></article><article className="highlight"><span>Forecast accuracy</span><strong>{data.summary.accuracy.toFixed(2)}%</strong><small>Selected cutoff</small></article></section><section className="content-grid"><article className="panel"><div className="panel-heading"><div><h2>Forecast versus actual</h2><p>Matched generation periods</p></div></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={data.series}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="startTime" tickFormatter={timeLabel}/><YAxis/><Tooltip labelFormatter={(value) => new Date(value).toLocaleString()}/><Legend/><Line dataKey="forecast" name="Forecast" stroke="#2563eb" strokeWidth={3}/><Line dataKey="actual" name="Actual" stroke="#10b981" strokeWidth={3}/></LineChart></ResponsiveContainer></div></article><article className="panel"><div className="panel-heading"><div><h2>Generation detail</h2><p>Latest eligible forecast per period</p></div></div><div className="table-wrap"><table><thead><tr><th>Time</th><th>Forecast</th><th>Actual</th><th>Error</th></tr></thead><tbody>{data.series.map((item) => <tr key={item.startTime}><td>{timeLabel(item.startTime)}</td><td>{number(item.forecast)}</td><td>{number(item.actual)}</td><td className={item.error >= 0 ? 'positive' : 'negative'}>{item.error >= 0 ? '+' : ''}{number(item.error)}</td></tr>)}</tbody></table></div></article></section></>}
  </main>
}
