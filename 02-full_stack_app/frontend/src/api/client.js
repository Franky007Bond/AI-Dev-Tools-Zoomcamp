import { getDefaultBackend } from './mockBackend.js'

export function createApi(backend) {
  return {
    getSnapshot: (now) => Promise.resolve(backend.getSnapshot(now)),
    addParty: (input, now) => Promise.resolve(backend.addParty(input, now)),
    updateParty: (id, patch, now) => Promise.resolve(backend.updateParty(id, patch, now)),
    removeParty: (id, now) => Promise.resolve(backend.removeParty(id, now)),
    reorderQueue: (fromPosition, toPosition, now) =>
      Promise.resolve(backend.reorderQueue(fromPosition, toPosition, now)),
    notifyReady: (partyId, now) => Promise.resolve(backend.notifyReady(partyId, now)),
    smsReply: (partyId, reply, now) => Promise.resolve(backend.smsReply(partyId, reply, now)),
    seatParty: (partyId, tableId, now) =>
      Promise.resolve(backend.seatParty(partyId, tableId, now)),
    setTableStatus: (tableId, status, now) =>
      Promise.resolve(backend.setTableStatus(tableId, status, now)),
    getAnalytics: (range, now) => Promise.resolve(backend.getAnalytics(range, now)),
    updateSettings: (patch, now) => Promise.resolve(backend.updateSettings(patch, now)),
    resetDemo: (now) => Promise.resolve(backend.resetDemo(now)),
  }
}

export const api = createApi(getDefaultBackend())
