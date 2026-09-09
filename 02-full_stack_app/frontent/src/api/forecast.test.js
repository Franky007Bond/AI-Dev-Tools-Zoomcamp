import { describe, expect, it } from 'vitest'
import { AVERAGE_DINING_MINUTES, estimateWaitMinutes } from './forecast.js'

const tables = [
  { id: 't1', seats: 2, status: 'free', occupiedAt: null },
  { id: 't2', seats: 4, status: 'occupied', occupiedAt: '2026-09-09T18:00:00.000Z' },
]

describe('estimateWaitMinutes', () => {
  it('returns a short wait when a fitting table is free and nobody is ahead', () => {
    expect(
      estimateWaitMinutes({
        partySize: 2,
        queueAhead: [],
        tables,
        now: Date.parse('2026-09-09T18:10:00.000Z'),
      }),
    ).toBe(5)
  })

  it('adds time for each party already waiting for the free table', () => {
    expect(
      estimateWaitMinutes({
        partySize: 2,
        queueAhead: [{ partySize: 2 }],
        tables: [
          ...tables,
          { id: 't3', seats: 2, status: 'free', occupiedAt: null },
        ],
        now: Date.parse('2026-09-09T18:10:00.000Z'),
      }),
    ).toBe(10)
  })

  it('uses remaining dining time when no free table fits', () => {
    const wait = estimateWaitMinutes({
      partySize: 4,
      queueAhead: [],
      tables,
      now: Date.parse('2026-09-09T18:10:00.000Z'),
    })
    expect(wait).toBe(AVERAGE_DINING_MINUTES - 10)
  })

  it('returns 90 minutes when no table is large enough', () => {
    expect(
      estimateWaitMinutes({
        partySize: 12,
        queueAhead: [],
        tables,
      }),
    ).toBe(90)
  })
})
