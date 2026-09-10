import { withWaitEstimates } from './forecast.js'

export const STORAGE_KEY = 'waitly.mock.v1'

const WAITING_STATUSES = new Set(['waiting', 'notified', 'confirmed'])

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function startOfDay(timestamp) {
  const date = new Date(timestamp)
  date.setHours(0, 0, 0, 0)
  return date.getTime()
}

function hourLabel(hour) {
  const suffix = hour >= 12 ? 'pm' : 'am'
  const normalized = hour % 12 || 12
  return `${normalized}${suffix}`
}

export function createSeedState(now = Date.now()) {
  const tables = [
    { id: 't1', name: 'T1', seats: 2, x: 8, y: 12, w: 16, h: 18 },
    { id: 't2', name: 'T2', seats: 2, x: 8, y: 42, w: 16, h: 18 },
    { id: 't3', name: 'T3', seats: 4, x: 30, y: 12, w: 18, h: 22 },
    { id: 't4', name: 'T4', seats: 4, x: 30, y: 48, w: 18, h: 22 },
    { id: 't5', name: 'T5', seats: 4, x: 54, y: 12, w: 18, h: 22 },
    { id: 't6', name: 'T6', seats: 6, x: 54, y: 48, w: 22, h: 26 },
    { id: 't7', name: 'T7', seats: 2, x: 80, y: 12, w: 16, h: 18 },
    { id: 't8', name: 'T8', seats: 8, x: 78, y: 46, w: 18, h: 32 },
  ]

  const parties = [
    {
      id: 'p1',
      name: 'Nguyen',
      phone: '555-0101',
      partySize: 2,
      notes: 'Window if possible',
      source: 'walk-in',
      status: 'waiting',
      position: 1,
      queuedAt: new Date(now - 18 * 60000).toISOString(),
      reservationTime: null,
      tableId: null,
      notifiedAt: null,
    },
    {
      id: 'p2',
      name: 'Patel',
      phone: '555-0102',
      partySize: 4,
      notes: '',
      source: 'remote',
      status: 'waiting',
      position: 2,
      queuedAt: new Date(now - 11 * 60000).toISOString(),
      reservationTime: null,
      tableId: null,
      notifiedAt: null,
    },
    {
      id: 'p3',
      name: 'Garcia',
      phone: '555-0103',
      partySize: 6,
      notes: 'Birthday',
      source: 'walk-in',
      status: 'notified',
      position: 3,
      queuedAt: new Date(now - 28 * 60000).toISOString(),
      reservationTime: null,
      tableId: null,
      notifiedAt: new Date(now - 2 * 60000).toISOString(),
    },
    {
      id: 'p4',
      name: 'Okoye',
      phone: '555-0104',
      partySize: 4,
      notes: 'Anniversary',
      source: 'reservation',
      status: 'waiting',
      position: 4,
      queuedAt: new Date(now - 5 * 60000).toISOString(),
      reservationTime: new Date(now - 5 * 60000).toISOString(),
      tableId: 't5',
      notifiedAt: null,
    },
    {
      id: 'p5',
      name: 'Berg',
      phone: '555-0105',
      partySize: 2,
      notes: '',
      source: 'walk-in',
      status: 'seated',
      position: null,
      queuedAt: new Date(now - 50 * 60000).toISOString(),
      reservationTime: null,
      tableId: 't1',
      notifiedAt: null,
      seatedAt: new Date(now - 22 * 60000).toISOString(),
      seatedWaitMinutes: 28,
    },
    {
      id: 'p6',
      name: 'Chen',
      phone: '555-0106',
      partySize: 4,
      notes: '',
      source: 'walk-in',
      status: 'seated',
      position: null,
      queuedAt: new Date(now - 70 * 60000).toISOString(),
      reservationTime: null,
      tableId: 't4',
      notifiedAt: null,
      seatedAt: new Date(now - 40 * 60000).toISOString(),
      seatedWaitMinutes: 30,
    },
  ]

  const tableState = {
    t1: { status: 'occupied', partyId: 'p5', occupiedAt: new Date(now - 22 * 60000).toISOString() },
    t2: { status: 'free', partyId: null, occupiedAt: null },
    t3: { status: 'free', partyId: null, occupiedAt: null },
    t4: { status: 'occupied', partyId: 'p6', occupiedAt: new Date(now - 40 * 60000).toISOString() },
    t5: { status: 'reserved', partyId: 'p4', occupiedAt: null },
    t6: { status: 'free', partyId: null, occupiedAt: null },
    t7: { status: 'free', partyId: null, occupiedAt: null },
    t8: { status: 'free', partyId: null, occupiedAt: null },
  }

  const sms = [
    {
      id: 's1',
      partyId: 'p1',
      direction: 'outbound',
      kind: 'join',
      body: 'Waitly: Nguyen party of 2 is on the list. Estimated wait 10 min.',
      at: new Date(now - 18 * 60000).toISOString(),
    },
    {
      id: 's2',
      partyId: 'p2',
      direction: 'outbound',
      kind: 'join',
      body: 'Waitly: Patel party of 4 is on the list. Estimated wait 20 min.',
      at: new Date(now - 11 * 60000).toISOString(),
    },
    {
      id: 's3',
      partyId: 'p3',
      direction: 'outbound',
      kind: 'join',
      body: 'Waitly: Garcia party of 6 is on the list. Estimated wait 25 min.',
      at: new Date(now - 28 * 60000).toISOString(),
    },
    {
      id: 's4',
      partyId: 'p3',
      direction: 'outbound',
      kind: 'ready',
      body: 'Waitly: Garcia, your table is ready. Reply YES to confirm or CANCEL to drop off.',
      at: new Date(now - 2 * 60000).toISOString(),
    },
    {
      id: 's5',
      partyId: 'p4',
      direction: 'outbound',
      kind: 'join',
      body: 'Waitly: Reservation for Okoye party of 4 is holding T5.',
      at: new Date(now - 5 * 60000).toISOString(),
    },
  ]

  const events = [
    {
      id: 'e1',
      type: 'seated',
      at: new Date(now - 3 * 3600000).toISOString(),
      waitMinutes: 12,
      hour: new Date(now - 3 * 3600000).getHours(),
    },
    {
      id: 'e2',
      type: 'seated',
      at: new Date(now - 2 * 3600000).toISOString(),
      waitMinutes: 22,
      hour: new Date(now - 2 * 3600000).getHours(),
    },
    {
      id: 'e3',
      type: 'no-show',
      at: new Date(now - 90 * 60000).toISOString(),
      waitMinutes: null,
      hour: new Date(now - 90 * 60000).getHours(),
    },
    {
      id: 'e4',
      type: 'seated',
      at: new Date(now - 40 * 60000).toISOString(),
      waitMinutes: 30,
      hour: new Date(now - 40 * 60000).getHours(),
    },
    {
      id: 'e5',
      type: 'seated',
      at: new Date(now - 22 * 60000).toISOString(),
      waitMinutes: 28,
      hour: new Date(now - 22 * 60000).getHours(),
    },
    {
      id: 'e6',
      type: 'seated',
      at: new Date(now - 26 * 3600000).toISOString(),
      waitMinutes: 18,
      hour: new Date(now - 26 * 3600000).getHours(),
    },
  ]

  return {
    nextId: 20,
    settings: {
      restaurantName: 'Waitly Bistro',
      gracePeriodMinutes: 8,
    },
    tables,
    tableState,
    parties,
    sms,
    events,
    hostNotices: [
      {
        id: 'n1',
        at: new Date(now - 2 * 60000).toISOString(),
        text: 'Garcia was texted that their table is ready.',
      },
    ],
  }
}

function compactQueue(parties) {
  const waiting = parties
    .filter((party) => WAITING_STATUSES.has(party.status))
    .sort((a, b) => a.position - b.position)

  waiting.forEach((party, index) => {
    party.position = index + 1
  })
}

export function summarizeAnalytics(events, { range = 'daily', now = Date.now() } = {}) {
  const start = range === 'weekly' ? now - 7 * 24 * 3600000 : startOfDay(now)
  const inRange = events.filter((event) => {
    const at = new Date(event.at).getTime()
    return at >= start && at <= now
  })

  const seated = inRange.filter((event) => event.type === 'seated')
  const noshows = inRange.filter((event) => event.type === 'no-show')
  const avgWait = seated.length
    ? seated.reduce((sum, event) => sum + event.waitMinutes, 0) / seated.length
    : 0
  const outcomeCount = seated.length + noshows.length

  const hours = Array.from({ length: 24 }, (_, hour) => ({
    hour,
    label: hourLabel(hour),
    count: 0,
  }))
  for (const event of inRange) {
    hours[new Date(event.at).getHours()].count += 1
  }

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const days = dayNames.map((label, weekday) => ({ weekday, label, count: 0 }))
  for (const event of inRange) {
    days[new Date(event.at).getDay()].count += 1
  }

  return {
    range,
    averageWaitMinutes: Math.round(avgWait),
    partiesSeated: seated.length,
    noShowRate: outcomeCount === 0 ? 0 : noshows.length / outcomeCount,
    busiestHours: hours.filter((row) => row.count > 0 || (row.hour >= 11 && row.hour <= 21)),
    busiestDays: days,
  }
}

export function createMockBackend({ persist = false, now = Date.now() } = {}) {
  let state = createSeedState(now)
  let seq = state.nextId

  function nextId(prefix) {
    seq += 1
    return `${prefix}${seq}`
  }

  function persistState() {
    if (!persist || typeof localStorage === 'undefined') return
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...state, nextId: seq }))
  }

  function loadPersisted() {
    if (!persist || typeof localStorage === 'undefined') return
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    try {
      const parsed = JSON.parse(raw)
      state = parsed
      seq = parsed.nextId ?? 20
    } catch {
      state = createSeedState(now)
    }
  }

  loadPersisted()

  function tablesView() {
    return state.tables.map((table) => {
      const extra = state.tableState[table.id]
      const party = extra.partyId
        ? state.parties.find((item) => item.id === extra.partyId)
        : null
      return {
        ...table,
        status: extra.status,
        partyId: extra.partyId,
        occupiedAt: extra.occupiedAt,
        partyName: party?.name ?? null,
      }
    })
  }

  function activateDueReservations(clock) {
    for (const party of state.parties) {
      if (
        party.source === 'reservation' &&
        party.status === 'upcoming' &&
        party.reservationTime &&
        new Date(party.reservationTime).getTime() <= clock
      ) {
        const lastPosition = state.parties.reduce(
          (max, item) =>
            WAITING_STATUSES.has(item.status) ? Math.max(max, item.position ?? 0) : max,
          0,
        )
        party.status = 'waiting'
        party.position = lastPosition + 1
        party.queuedAt = party.reservationTime
      }
    }
  }

  function applyNoShows(clock) {
    const graceMs = state.settings.gracePeriodMinutes * 60000
    const removed = []

    for (const party of state.parties) {
      if (party.status !== 'notified' || !party.notifiedAt) continue
      if (clock - new Date(party.notifiedAt).getTime() < graceMs) continue

      party.status = 'no-show'
      party.position = null
      if (party.tableId && state.tableState[party.tableId]?.partyId === party.id) {
        state.tableState[party.tableId] = {
          status: 'free',
          partyId: null,
          occupiedAt: null,
        }
      }
      party.tableId = null
      state.events.push({
        id: nextId('e'),
        type: 'no-show',
        at: new Date(clock).toISOString(),
        waitMinutes: null,
        hour: new Date(clock).getHours(),
      })
      state.sms.push({
        id: nextId('s'),
        partyId: party.id,
        direction: 'outbound',
        kind: 'noshow',
        body: `Waitly: ${party.name} was removed after the grace period. Reply if this was a mistake.`,
        at: new Date(clock).toISOString(),
      })
      state.hostNotices.unshift({
        id: nextId('n'),
        at: new Date(clock).toISOString(),
        text: `${party.name} was auto-removed as a no-show.`,
      })
      removed.push(party.id)
    }

    if (removed.length) compactQueue(state.parties)
    return removed
  }

  function snapshot(clock = Date.now()) {
    activateDueReservations(clock)
    applyNoShows(clock)
    compactQueue(state.parties)
    const tables = tablesView()
    const parties = withWaitEstimates(clone(state.parties), tables, clock)
    persistState()

    return {
      now: new Date(clock).toISOString(),
      settings: { ...state.settings },
      tables,
      parties,
      queue: parties
        .filter((party) => WAITING_STATUSES.has(party.status))
        .sort((a, b) => a.position - b.position),
      upcoming: parties
        .filter((party) => party.status === 'upcoming')
        .sort(
          (a, b) =>
            new Date(a.reservationTime).getTime() - new Date(b.reservationTime).getTime(),
        ),
      sms: clone(state.sms).sort((a, b) => new Date(b.at) - new Date(a.at)),
      hostNotices: clone(state.hostNotices).slice(0, 8),
    }
  }

  function requireParty(id) {
    const party = state.parties.find((item) => item.id === id)
    if (!party) throw new Error(`Party ${id} not found`)
    return party
  }

  function addSms(party, kind, body, clock, direction = 'outbound') {
    state.sms.push({
      id: nextId('s'),
      partyId: party.id,
      direction,
      kind,
      body,
      at: new Date(clock).toISOString(),
    })
  }

  return {
    getSnapshot(clock = Date.now()) {
      return snapshot(clock)
    },

    addParty(input, clock = Date.now()) {
      const source = input.source ?? 'walk-in'
      const isFutureReservation =
        source === 'reservation' &&
        input.reservationTime &&
        new Date(input.reservationTime).getTime() > clock

      const party = {
        id: nextId('p'),
        name: input.name.trim(),
        phone: input.phone.trim(),
        partySize: Number(input.partySize),
        notes: (input.notes ?? '').trim(),
        source,
        status: isFutureReservation ? 'upcoming' : 'waiting',
        position: null,
        queuedAt: new Date(clock).toISOString(),
        reservationTime: input.reservationTime ?? null,
        tableId: input.tableId ?? null,
        notifiedAt: null,
      }

      if (!isFutureReservation) {
        const lastPosition = state.parties.reduce(
          (max, item) =>
            WAITING_STATUSES.has(item.status) ? Math.max(max, item.position ?? 0) : max,
          0,
        )
        party.position = lastPosition + 1
      }

      if (party.tableId) {
        const table = state.tableState[party.tableId]
        if (!table || table.status !== 'free') {
          throw new Error('Reservation table is not free')
        }
        state.tableState[party.tableId] = {
          status: 'reserved',
          partyId: party.id,
          occupiedAt: null,
        }
      }

      state.parties.push(party)
      const preview = snapshot(clock)
      const created = preview.parties.find((item) => item.id === party.id)
      const wait = created?.waitEstimateMinutes
      addSms(
        party,
        'join',
        source === 'reservation'
          ? `Waitly: Reservation for ${party.name} party of ${party.partySize}${party.tableId ? ' is holding a table' : ''}.`
          : `Waitly: ${party.name} party of ${party.partySize} is on the list.${wait ? ` Estimated wait ${wait} min.` : ''}`,
        clock,
      )
      return snapshot(clock)
    },

    updateParty(id, patch, clock = Date.now()) {
      const party = requireParty(id)
      if (patch.name != null) party.name = patch.name.trim()
      if (patch.phone != null) party.phone = patch.phone.trim()
      if (patch.partySize != null) party.partySize = Number(patch.partySize)
      if (patch.notes != null) party.notes = patch.notes.trim()
      if (patch.reservationTime != null) party.reservationTime = patch.reservationTime
      return snapshot(clock)
    },

    removeParty(id, clock = Date.now()) {
      const party = requireParty(id)
      party.status = 'cancelled'
      party.position = null
      if (party.tableId && state.tableState[party.tableId]?.partyId === party.id) {
        state.tableState[party.tableId] = {
          status: 'free',
          partyId: null,
          occupiedAt: null,
        }
      }
      party.tableId = null
      addSms(party, 'cancel', `Waitly: ${party.name} was removed from the waitlist.`, clock)
      return snapshot(clock)
    },

    reorderQueue(fromPosition, toPosition, clock = Date.now()) {
      const queue = state.parties
        .filter((party) => WAITING_STATUSES.has(party.status))
        .sort((a, b) => a.position - b.position)
      const fromIndex = fromPosition - 1
      const toIndex = toPosition - 1
      if (fromIndex < 0 || toIndex < 0 || fromIndex >= queue.length || toIndex >= queue.length) {
        throw new Error('Invalid queue position')
      }
      const [moved] = queue.splice(fromIndex, 1)
      queue.splice(toIndex, 0, moved)
      queue.forEach((party, index) => {
        party.position = index + 1
      })
      return snapshot(clock)
    },

    notifyReady(partyId, clock = Date.now()) {
      const party = requireParty(partyId)
      if (!WAITING_STATUSES.has(party.status)) {
        throw new Error('Party is not waiting')
      }
      party.status = 'notified'
      party.notifiedAt = new Date(clock).toISOString()
      addSms(
        party,
        'ready',
        `Waitly: ${party.name}, your table is ready. Reply YES to confirm or CANCEL to drop off.`,
        clock,
      )
      state.hostNotices.unshift({
        id: nextId('n'),
        at: new Date(clock).toISOString(),
        text: `${party.name} was texted that their table is ready.`,
      })
      return snapshot(clock)
    },

    smsReply(partyId, reply, clock = Date.now()) {
      const party = requireParty(partyId)
      const normalized = String(reply).trim().toLowerCase()
      if (normalized === 'yes' || normalized === 'confirm') {
        party.status = 'confirmed'
        addSms(party, 'confirm', 'YES', clock, 'inbound')
        addSms(party, 'confirm', `Waitly: Thanks ${party.name}, see you shortly.`, clock)
        return snapshot(clock)
      }
      if (normalized === 'cancel') {
        addSms(party, 'cancel', 'CANCEL', clock, 'inbound')
        return this.removeParty(partyId, clock)
      }
      throw new Error('Reply must be YES or CANCEL')
    },

    seatParty(partyId, tableId, clock = Date.now()) {
      const party = requireParty(partyId)
      const table = state.tableState[tableId]
      if (!table) throw new Error('Table not found')
      if (table.status === 'occupied') throw new Error('Table is occupied')
      if (table.status === 'reserved' && table.partyId !== partyId) {
        throw new Error('Table is reserved for another party')
      }

      if (party.tableId && party.tableId !== tableId) {
        const previous = state.tableState[party.tableId]
        if (previous?.partyId === partyId) {
          state.tableState[party.tableId] = {
            status: 'free',
            partyId: null,
            occupiedAt: null,
          }
        }
      }

      const waitMinutes = Math.max(
        0,
        Math.round((clock - new Date(party.queuedAt).getTime()) / 60000),
      )
      party.status = 'seated'
      party.position = null
      party.tableId = tableId
      party.seatedAt = new Date(clock).toISOString()
      party.seatedWaitMinutes = waitMinutes
      state.tableState[tableId] = {
        status: 'occupied',
        partyId,
        occupiedAt: new Date(clock).toISOString(),
      }
      state.events.push({
        id: nextId('e'),
        type: 'seated',
        at: new Date(clock).toISOString(),
        waitMinutes,
        hour: new Date(clock).getHours(),
      })
      addSms(
        party,
        'seated',
        `Waitly: ${party.name} is seated at ${state.tables.find((item) => item.id === tableId).name}.`,
        clock,
      )
      return snapshot(clock)
    },

    setTableStatus(tableId, status, clock = Date.now()) {
      const table = state.tableState[tableId]
      if (!table) throw new Error('Table not found')
      if (status === 'occupied') {
        state.tableState[tableId] = {
          status: 'occupied',
          partyId: table.partyId,
          occupiedAt: table.occupiedAt ?? new Date(clock).toISOString(),
        }
        return snapshot(clock)
      }
      if (status === 'free') {
        const previousPartyId = table.partyId
        state.tableState[tableId] = { status: 'free', partyId: null, occupiedAt: null }
        const reservedParty = state.parties.find(
          (party) => party.id === previousPartyId && party.source === 'reservation' && WAITING_STATUSES.has(party.status),
        )
        if (reservedParty) reservedParty.tableId = null

        const freed = snapshot(clock)
        const tableView = freed.tables.find((item) => item.id === tableId)
        const nextParty = freed.queue.find(
          (party) =>
            party.status === 'waiting' &&
            party.partySize <= (state.tables.find((item) => item.id === tableId)?.seats ?? 0) &&
            (!party.tableId || party.tableId === tableId),
        )
        if (nextParty && tableView.status === 'free') {
          return this.notifyReady(nextParty.id, clock)
        }
        return freed
      }
      if (status === 'reserved') {
        state.tableState[tableId] = {
          status: 'reserved',
          partyId: table.partyId,
          occupiedAt: null,
        }
        return snapshot(clock)
      }
      throw new Error('Unknown table status')
    },

    getAnalytics(range = 'daily', clock = Date.now()) {
      snapshot(clock)
      return summarizeAnalytics(state.events, { range, now: clock })
    },

    updateSettings(patch, clock = Date.now()) {
      state.settings = { ...state.settings, ...patch }
      return snapshot(clock)
    },

    resetDemo(clock = Date.now()) {
      state = createSeedState(clock)
      seq = state.nextId
      if (persist && typeof localStorage !== 'undefined') {
        localStorage.removeItem(STORAGE_KEY)
      }
      return snapshot(clock)
    },
  }
}

let defaultBackend

export function getDefaultBackend() {
  if (!defaultBackend) {
    defaultBackend = createMockBackend({ persist: true })
  }
  return defaultBackend
}
