import { useMemo, useState } from 'react'
import AnalyticsPanel from '../components/AnalyticsPanel.jsx'
import FloorPlan from '../components/FloorPlan.jsx'
import PartyForm from '../components/PartyForm.jsx'
import QueuePanel from '../components/QueuePanel.jsx'
import SettingsPanel from '../components/SettingsPanel.jsx'
import SmsPanel from '../components/SmsPanel.jsx'
import { useWaitly } from '../hooks/useWaitly.js'
import { toDatetimeLocal } from '../format.js'

const VIEWS = [
  { id: 'board', label: 'Board' },
  { id: 'sms', label: 'SMS' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'settings', label: 'Settings' },
]

export default function HostStand({ api }) {
  const waitly = useWaitly(api)
  const [view, setView] = useState('board')
  const [modal, setModal] = useState(null)
  const [selectedPartyId, setSelectedPartyId] = useState(null)
  const [tableSheet, setTableSheet] = useState(null)

  const snapshot = waitly.snapshot
  const selectedParty = useMemo(
    () => snapshot?.parties.find((party) => party.id === selectedPartyId) ?? null,
    [snapshot, selectedPartyId],
  )

  if (!snapshot) {
    return (
      <main className="host-app">
        <p className="loading">Loading host stand…</p>
      </main>
    )
  }

  return (
    <div className="host-app">
      <header className="topbar">
        <div>
          <p className="eyebrow">Host stand</p>
          <h1>{snapshot.settings.restaurantName}</h1>
        </div>
        <nav className="tabs" aria-label="Host views">
          {VIEWS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={view === item.id ? 'active' : ''}
              onClick={() => setView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <p className="status-pill">{snapshot.queue.length} in queue</p>
      </header>

      {waitly.error ? <p className="banner error">{waitly.error}</p> : null}
      {snapshot.hostNotices[0] ? (
        <p className="banner notice">{snapshot.hostNotices[0].text}</p>
      ) : null}

      {view === 'board' ? (
        <div className="board">
          <QueuePanel
            queue={snapshot.queue}
            upcoming={snapshot.upcoming}
            tables={snapshot.tables}
            selectedPartyId={selectedPartyId}
            onSelectParty={setSelectedPartyId}
            onAdd={() => setModal({ type: 'add' })}
            onEdit={(party) => setModal({ type: 'edit', party })}
            onRemove={(id) => waitly.run(() => api.removeParty(id))}
            onMove={(from, to) => waitly.run(() => api.reorderQueue(from, to))}
            onNotify={(id) => waitly.run(() => api.notifyReady(id))}
            onSeat={(partyId, tableId) => {
              waitly.run(() => api.seatParty(partyId, tableId))
              setSelectedPartyId(null)
            }}
          />
          <FloorPlan
            tables={snapshot.tables}
            queue={snapshot.queue}
            selectedPartyId={selectedPartyId}
            onSeat={(partyId, tableId) => {
              waitly.run(() => api.seatParty(partyId, tableId))
              setSelectedPartyId(null)
            }}
            onSelectTable={setTableSheet}
          />
        </div>
      ) : null}

      {view === 'sms' ? (
        <SmsPanel
          sms={snapshot.sms}
          parties={snapshot.parties}
          onReply={(partyId, reply) => waitly.run(() => api.smsReply(partyId, reply))}
        />
      ) : null}

      {view === 'analytics' ? (
        <AnalyticsPanel
          analytics={waitly.analytics}
          range={waitly.analyticsRange}
          onRangeChange={waitly.setAnalyticsRange}
        />
      ) : null}

      {view === 'settings' ? (
        <SettingsPanel
          settings={snapshot.settings}
          onSave={(patch) => waitly.run(() => api.updateSettings(patch))}
          onReset={() => waitly.run(() => api.resetDemo())}
        />
      ) : null}

      {modal ? (
        <div className="modal-backdrop" role="presentation" onClick={() => setModal(null)}>
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label={modal.type === 'edit' ? 'Edit party' : 'Add party'}
            onClick={(event) => event.stopPropagation()}
          >
            <PartyForm
              title={modal.type === 'edit' ? 'Edit party' : 'Add party'}
              submitLabel={modal.type === 'edit' ? 'Save' : 'Add to queue'}
              showReservationFields={modal.type === 'add'}
              tables={snapshot.tables}
              initial={
                modal.party
                  ? {
                      ...modal.party,
                      reservationTimeLocal: toDatetimeLocal(modal.party.reservationTime),
                    }
                  : {}
              }
              onCancel={() => setModal(null)}
              onSubmit={async (input) => {
                if (modal.type === 'edit') {
                  await waitly.run(() => api.updateParty(modal.party.id, input))
                } else {
                  await waitly.run(() => api.addParty(input))
                }
                setModal(null)
              }}
            />
          </div>
        </div>
      ) : null}

      {tableSheet ? (
        <div className="modal-backdrop" role="presentation" onClick={() => setTableSheet(null)}>
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label={`${tableSheet.name} actions`}
            onClick={(event) => event.stopPropagation()}
          >
            <h3>
              {tableSheet.name} · {tableSheet.seats} seats
            </h3>
            <p className="hint">
              Status: {tableSheet.status}
              {tableSheet.partyName ? ` · ${tableSheet.partyName}` : ''}
            </p>
            <div className="form-actions wrap">
              {tableSheet.status !== 'free' ? (
                <button
                  type="button"
                  className="btn primary"
                  onClick={() => {
                    waitly.run(() => api.setTableStatus(tableSheet.id, 'free'))
                    setTableSheet(null)
                  }}
                >
                  Mark free
                </button>
              ) : null}
              {tableSheet.status === 'free' ? (
                <button
                  type="button"
                  className="btn"
                  onClick={() => {
                    waitly.run(() => api.setTableStatus(tableSheet.id, 'occupied'))
                    setTableSheet(null)
                  }}
                >
                  Mark occupied
                </button>
              ) : null}
              {selectedParty && tableSheet.status !== 'occupied' ? (
                <button
                  type="button"
                  className="btn primary"
                  onClick={() => {
                    waitly.run(() => api.seatParty(selectedParty.id, tableSheet.id))
                    setSelectedPartyId(null)
                    setTableSheet(null)
                  }}
                >
                  Seat {selectedParty.name} here
                </button>
              ) : null}
              <button type="button" className="btn ghost" onClick={() => setTableSheet(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
