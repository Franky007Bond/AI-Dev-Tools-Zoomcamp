import { describe, expect, it } from 'vitest'
import { createMockBackend } from './mockBackend.js'
import { createApi } from './client.js'

const NOW = Date.parse('2026-09-09T19:00:00.000Z')

function apiAt(now = NOW) {
  return createApi(createMockBackend({ persist: false, now }))
}

describe('mock API', () => {
  it('loads a unified queue with wait estimates', async () => {
    const api = apiAt()
    const snap = await api.getSnapshot(NOW)
    expect(snap.queue.map((party) => party.name)).toEqual(['Nguyen', 'Patel', 'Garcia', 'Okoye'])
    expect(snap.queue[0].waitEstimateMinutes).toBeGreaterThan(0)
    expect(snap.tables.find((table) => table.id === 't5').status).toBe('reserved')
  })

  it('adds a walk-in and sends a join SMS', async () => {
    const api = apiAt()
    const snap = await api.addParty(
      { name: 'Rivera', phone: '555-0199', partySize: 3, notes: '', source: 'walk-in' },
      NOW,
    )
    expect(snap.queue.at(-1).name).toBe('Rivera')
    expect(snap.sms[0].body).toMatch(/Rivera party of 3/)
  })

  it('keeps a future reservation off the live queue and holds its table', async () => {
    const api = apiAt()
    const later = new Date(NOW + 2 * 3600000).toISOString()
    const snap = await api.addParty(
      {
        name: 'Adler',
        phone: '555-0188',
        partySize: 2,
        source: 'reservation',
        reservationTime: later,
        tableId: 't2',
      },
      NOW,
    )
    expect(snap.queue.some((party) => party.name === 'Adler')).toBe(false)
    expect(snap.upcoming[0].name).toBe('Adler')
    expect(snap.tables.find((table) => table.id === 't2').status).toBe('reserved')

    const due = await api.getSnapshot(NOW + 2 * 3600000)
    expect(due.queue.some((party) => party.name === 'Adler')).toBe(true)
  })

  it('reorders, edits, and removes parties', async () => {
    const api = apiAt()
    let snap = await api.reorderQueue(1, 2, NOW)
    expect(snap.queue.map((party) => party.name).slice(0, 2)).toEqual(['Patel', 'Nguyen'])
    snap = await api.updateParty('p2', { notes: 'High chair' }, NOW)
    expect(snap.parties.find((party) => party.id === 'p2').notes).toBe('High chair')
    snap = await api.removeParty('p2', NOW)
    expect(snap.queue.some((party) => party.id === 'p2')).toBe(false)
  })

  it('seats a party onto a free fitting table', async () => {
    const api = apiAt()
    const snap = await api.seatParty('p1', 't2', NOW)
    expect(snap.queue.some((party) => party.id === 'p1')).toBe(false)
    const table = snap.tables.find((item) => item.id === 't2')
    expect(table.status).toBe('occupied')
    expect(table.partyName).toBe('Nguyen')
  })

  it('records guest SMS confirm and cancel', async () => {
    const api = apiAt()
    let snap = await api.smsReply('p3', 'YES', NOW)
    expect(snap.queue.find((party) => party.id === 'p3').status).toBe('confirmed')
    snap = await api.notifyReady('p1', NOW)
    snap = await api.smsReply('p1', 'CANCEL', NOW)
    expect(snap.queue.some((party) => party.id === 'p1')).toBe(false)
  })

  it('auto-removes a notified party after the grace period', async () => {
    const api = apiAt()
    const later = NOW + 8 * 60000
    const snap = await api.getSnapshot(later)
    expect(snap.queue.some((party) => party.id === 'p3')).toBe(false)
    expect(snap.parties.find((party) => party.id === 'p3').status).toBe('no-show')
    expect(snap.hostNotices[0].text).toMatch(/no-show/)
  })

  it('summarizes daily analytics', async () => {
    const api = apiAt()
    const analytics = await api.getAnalytics('daily', NOW)
    expect(analytics.partiesSeated).toBeGreaterThan(0)
    expect(analytics.averageWaitMinutes).toBeGreaterThan(0)
    expect(analytics.noShowRate).toBeGreaterThanOrEqual(0)
    expect(analytics.busiestHours.some((row) => row.count > 0)).toBe(true)
  })
})
