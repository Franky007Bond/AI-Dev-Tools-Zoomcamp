const DEFAULT_BASE = import.meta.env.VITE_API_BASE ?? '/v1'

async function readError(res) {
  try {
    const body = await res.json()
    if (body?.error) return body.error
  } catch {
    // ignore non-JSON bodies
  }
  return `Request failed (${res.status})`
}

export function createHttpBackend(baseUrl = DEFAULT_BASE) {
  const base = baseUrl.replace(/\/$/, '')

  async function request(path, options = {}) {
    const res = await fetch(`${base}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
    if (!res.ok) {
      throw new Error(await readError(res))
    }
    return res.json()
  }

  return {
    getSnapshot() {
      return request('/snapshot')
    },

    addParty(input) {
      return request('/parties', { method: 'POST', body: JSON.stringify(input) })
    },

    joinWaitlist(input) {
      const { name, phone, partySize, notes = '' } = input
      return request('/join', {
        method: 'POST',
        body: JSON.stringify({ name, phone, partySize, notes }),
      })
    },

    updateParty(id, patch) {
      return request(`/parties/${encodeURIComponent(id)}`, {
        method: 'PATCH',
        body: JSON.stringify(patch),
      })
    },

    removeParty(id) {
      return request(`/parties/${encodeURIComponent(id)}`, { method: 'DELETE' })
    },

    reorderQueue(fromPosition, toPosition) {
      return request('/queue/reorder', {
        method: 'POST',
        body: JSON.stringify({ fromPosition, toPosition }),
      })
    },

    notifyReady(partyId) {
      return request(`/parties/${encodeURIComponent(partyId)}/notify`, { method: 'POST' })
    },

    smsReply(partyId, reply) {
      return request(`/parties/${encodeURIComponent(partyId)}/sms-reply`, {
        method: 'POST',
        body: JSON.stringify({ reply }),
      })
    },

    seatParty(partyId, tableId) {
      return request(`/parties/${encodeURIComponent(partyId)}/seat`, {
        method: 'POST',
        body: JSON.stringify({ tableId }),
      })
    },

    setTableStatus(tableId, status) {
      return request(`/tables/${encodeURIComponent(tableId)}`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      })
    },

    getAnalytics(range = 'daily') {
      const query = new URLSearchParams({ range })
      return request(`/analytics?${query}`)
    },

    updateSettings(patch) {
      return request('/settings', { method: 'PATCH', body: JSON.stringify(patch) })
    },

    resetDemo() {
      return request('/demo/reset', { method: 'POST' })
    },
  }
}

export function getDefaultHttpBackend() {
  return createHttpBackend()
}
