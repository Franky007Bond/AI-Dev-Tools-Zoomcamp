import { useEffect, useState } from 'react'
import { STORAGE_KEY } from '../api/mockBackend.js'

export function useWaitly(api) {
  const [snapshot, setSnapshot] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [analyticsRange, setAnalyticsRange] = useState('daily')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function refresh(range = analyticsRange) {
    const [nextSnapshot, nextAnalytics] = await Promise.all([
      api.getSnapshot(),
      api.getAnalytics(range),
    ])
    setSnapshot(nextSnapshot)
    setAnalytics(nextAnalytics)
    return nextSnapshot
  }

  async function run(operation) {
    setBusy(true)
    setError('')
    try {
      const result = await operation()
      if (result && result.parties && result.tables) {
        setSnapshot(result)
        setAnalytics(await api.getAnalytics(analyticsRange))
        return result
      }
      return refresh()
    } catch (err) {
      setError(err.message ?? 'Something went wrong')
      throw err
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    refresh().catch((err) => setError(err.message ?? 'Failed to load'))
    const timer = setInterval(() => {
      refresh().catch(() => {})
    }, 4000)
    const onStorage = (event) => {
      if (event.key === STORAGE_KEY) refresh().catch(() => {})
    }
    window.addEventListener('storage', onStorage)
    return () => {
      clearInterval(timer)
      window.removeEventListener('storage', onStorage)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [api, analyticsRange])

  return {
    snapshot,
    analytics,
    analyticsRange,
    setAnalyticsRange,
    error,
    busy,
    run,
    refresh,
  }
}
