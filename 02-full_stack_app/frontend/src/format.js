export function formatWait(minutes) {
  if (minutes == null) return '—'
  if (minutes < 1) return '<1 min'
  return `${minutes} min`
}

export function formatTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

export function toDatetimeLocal(iso) {
  if (!iso) return ''
  const date = new Date(iso)
  const pad = (value) => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function fromDatetimeLocal(value) {
  if (!value) return null
  return new Date(value).toISOString()
}

export function sourceLabel(source) {
  if (source === 'reservation') return 'Reservation'
  if (source === 'remote') return 'QR / web'
  return 'Walk-in'
}

export function statusLabel(status) {
  if (status === 'notified') return 'Texted — ready'
  if (status === 'confirmed') return 'On the way'
  if (status === 'upcoming') return 'Upcoming'
  if (status === 'waiting') return 'Waiting'
  return status
}
