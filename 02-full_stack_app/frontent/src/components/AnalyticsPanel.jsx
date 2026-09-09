export default function AnalyticsPanel({ analytics, range, onRangeChange }) {
  if (!analytics) {
    return (
      <section className="panel" aria-label="Analytics">
        <p>Loading analytics…</p>
      </section>
    )
  }

  const bars = range === 'weekly' ? analytics.busiestDays : analytics.busiestHours
  const max = Math.max(1, ...bars.map((row) => row.count))

  return (
    <section className="panel analytics-panel" aria-label="Analytics">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Analytics</p>
          <h2>{range === 'weekly' ? 'This week' : 'Today'}</h2>
        </div>
        <div className="segmented" role="group" aria-label="Analytics range">
          <button
            type="button"
            className={range === 'daily' ? 'active' : ''}
            onClick={() => onRangeChange('daily')}
          >
            Daily
          </button>
          <button
            type="button"
            className={range === 'weekly' ? 'active' : ''}
            onClick={() => onRangeChange('weekly')}
          >
            Weekly
          </button>
        </div>
      </header>

      <div className="stat-grid">
        <article className="stat">
          <p>Average wait</p>
          <strong>{analytics.averageWaitMinutes} min</strong>
        </article>
        <article className="stat">
          <p>Parties seated</p>
          <strong>{analytics.partiesSeated}</strong>
        </article>
        <article className="stat">
          <p>No-show rate</p>
          <strong>{Math.round(analytics.noShowRate * 100)}%</strong>
        </article>
      </div>

      <h3>{range === 'weekly' ? 'Busiest days' : 'Busiest hours'}</h3>
      <ul className="bars">
        {bars.map((row) => (
          <li key={row.label}>
            <span>{row.label}</span>
            <span className="bar-track">
              <span
                className="bar-fill"
                style={{ width: `${(row.count / max) * 100}%` }}
              />
            </span>
            <span>{row.count}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
