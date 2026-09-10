export default function FloorPlan({ tables, selectedPartyId, queue, onSelectTable, onSeat }) {
  return (
    <section className="panel floor-panel" aria-label="Floor plan">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Floor plan</p>
          <h2>Dining room</h2>
        </div>
        <ul className="legend">
          <li><span className="dot free" /> Free</li>
          <li><span className="dot occupied" /> Occupied</li>
          <li><span className="dot reserved" /> Reserved</li>
        </ul>
      </header>
      <p className="hint">
        {selectedPartyId
          ? 'Click a free table to seat the selected party.'
          : 'Tap a table to change status, or select a party first to seat them.'}
      </p>
      <div className="room">
        {tables.map((table) => (
          <button
            key={table.id}
            type="button"
            className={`table ${table.status}`}
            style={{
              left: `${table.x}%`,
              top: `${table.y}%`,
              width: `${table.w}%`,
              height: `${table.h}%`,
            }}
            aria-label={`${table.name}, ${table.seats} seats, ${table.status}${table.partyName ? `, ${table.partyName}` : ''}`}
            onClick={() => {
              if (selectedPartyId && (table.status === 'free' || table.partyId === selectedPartyId)) {
                onSeat(selectedPartyId, table.id)
                return
              }
              onSelectTable(table)
            }}
          >
            <strong>{table.name}</strong>
            <span>{table.seats} top</span>
            <span className="table-status">{table.partyName ?? table.status}</span>
          </button>
        ))}
        <div className="host-stand">Host</div>
      </div>
      {selectedPartyId ? (
        <p className="hint">
          Seating {queue.find((party) => party.id === selectedPartyId)?.name ?? 'selected party'}
        </p>
      ) : null}
    </section>
  )
}
