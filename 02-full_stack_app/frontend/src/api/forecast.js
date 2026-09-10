export const AVERAGE_DINING_MINUTES = 45
export const MINUTES_PER_PARTY_AHEAD = 10
export const SEAT_NOW_MINUTES = 5

export function estimateWaitMinutes({
  partySize,
  queueAhead = [],
  tables = [],
  now = Date.now(),
}) {
  const fitting = tables.filter((table) => table.seats >= partySize)
  if (fitting.length === 0) {
    return 90
  }

  const free = fitting.filter((table) => table.status === 'free')
  const occupied = fitting.filter((table) => table.status === 'occupied')
  const ahead = queueAhead.length

  if (free.length > ahead) {
    return SEAT_NOW_MINUTES * (ahead + 1)
  }

  const remainingTurnover = occupied.map((table) => {
    const occupiedAt = table.occupiedAt ? new Date(table.occupiedAt).getTime() : now
    const elapsedMinutes = Math.max(0, (now - occupiedAt) / 60000)
    return Math.max(5, AVERAGE_DINING_MINUTES - elapsedMinutes)
  })

  const nextTableMinutes = remainingTurnover.length
    ? Math.min(...remainingTurnover)
    : AVERAGE_DINING_MINUTES

  return Math.round(
    nextTableMinutes + MINUTES_PER_PARTY_AHEAD * Math.max(0, ahead - free.length),
  )
}

export function withWaitEstimates(parties, tables, now = Date.now()) {
  const waiting = parties.filter((party) =>
    ['waiting', 'notified', 'confirmed'].includes(party.status),
  )

  return parties.map((party) => {
    if (!['waiting', 'notified', 'confirmed'].includes(party.status)) {
      return { ...party, waitEstimateMinutes: null }
    }

    const queueAhead = waiting.filter(
      (other) => other.position < party.position,
    )

    return {
      ...party,
      waitEstimateMinutes: estimateWaitMinutes({
        partySize: party.partySize,
        queueAhead,
        tables,
        now,
      }),
    }
  })
}
