import { formatTime, formatWait, sourceLabel, statusLabel } from '../format.js'

export default function QueuePanel({
  queue,
  upcoming,
  tables,
  selectedPartyId,
  onSelectParty,
  onAdd,
  onEdit,
  onRemove,
  onMove,
  onNotify,
  onSeat,
}) {
  return (
    <section className="panel queue-panel" aria-label="Waitlist">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Live queue</p>
          <h2>{queue.length} waiting</h2>
        </div>
        <button type="button" className="btn primary" onClick={onAdd}>
          Add party
        </button>
      </header>

      {queue.length === 0 ? (
        <p className="empty">Queue is clear. Add a walk-in or wait for a remote join.</p>
      ) : (
        <ol className="queue-list">
          {queue.map((party) => (
            <li key={party.id}>
              <article
                className={`ticket ${selectedPartyId === party.id ? 'selected' : ''} ${party.status}`}
              >
                <button
                  type="button"
                  className="ticket-main"
                  onClick={() => onSelectParty(party.id === selectedPartyId ? null : party.id)}
                >
                  <span className="position">{party.position}</span>
                  <span className="ticket-body">
                    <strong>
                      {party.name} · {party.partySize}
                    </strong>
                    <span className="meta">
                      {sourceLabel(party.source)} · {statusLabel(party.status)} · {party.phone}
                    </span>
                    {party.notes ? <span className="notes">{party.notes}</span> : null}
                  </span>
                  <span className="wait">
                    <span className="wait-value">{formatWait(party.waitEstimateMinutes)}</span>
                    <span className="wait-label">est. wait</span>
                  </span>
                </button>
                <div className="ticket-actions">
                  <button
                    type="button"
                    className="btn tiny"
                    aria-label={`Move ${party.name} up`}
                    disabled={party.position === 1}
                    onClick={() => onMove(party.position, party.position - 1)}
                  >
                    Up
                  </button>
                  <button
                    type="button"
                    className="btn tiny"
                    aria-label={`Move ${party.name} down`}
                    disabled={party.position === queue.length}
                    onClick={() => onMove(party.position, party.position + 1)}
                  >
                    Down
                  </button>
                  {party.status !== 'notified' && party.status !== 'confirmed' ? (
                    <button type="button" className="btn tiny" onClick={() => onNotify(party.id)}>
                      Table ready
                    </button>
                  ) : null}
                  <label className="seat-label">
                    Seat
                    <select
                      aria-label={`Seat ${party.name}`}
                      value=""
                      onChange={(event) => {
                        if (event.target.value) onSeat(party.id, event.target.value)
                      }}
                    >
                      <option value="">Table…</option>
                      {tables
                        .filter(
                          (table) =>
                            table.status === 'free' ||
                            (table.status === 'reserved' && table.partyId === party.id),
                        )
                        .filter((table) => table.seats >= party.partySize)
                        .map((table) => (
                          <option key={table.id} value={table.id}>
                            {table.name} ({table.seats})
                          </option>
                        ))}
                    </select>
                  </label>
                  <button type="button" className="btn tiny edit" onClick={() => onEdit(party)}>
                    Edit
                  </button>
                  <button type="button" className="btn tiny danger" onClick={() => onRemove(party.id)}>
                    Remove
                  </button>
                </div>
              </article>
            </li>
          ))}
        </ol>
      )}

      {upcoming.length > 0 ? (
        <div className="upcoming">
          <h3>Upcoming reservations</h3>
          <ul>
            {upcoming.map((party) => (
              <li key={party.id}>
                {formatTime(party.reservationTime)} · {party.name} · {party.partySize}
                {party.tableId ? ` · holding ${tables.find((table) => table.id === party.tableId)?.name}` : ''}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  )
}
