export default function PartyForm({
  title,
  submitLabel,
  initial = {},
  tables = [],
  showReservationFields = false,
  onSubmit,
  onCancel,
}) {
  return (
    <form
      className="party-form"
      onSubmit={(event) => {
        event.preventDefault()
        const data = new FormData(event.currentTarget)
        onSubmit({
          name: String(data.get('name') ?? ''),
          phone: String(data.get('phone') ?? ''),
          partySize: Number(data.get('partySize')),
          notes: String(data.get('notes') ?? ''),
          source: showReservationFields ? String(data.get('source') ?? 'walk-in') : initial.source,
          reservationTime: data.get('reservationTime')
            ? new Date(String(data.get('reservationTime'))).toISOString()
            : null,
          tableId: data.get('tableId') ? String(data.get('tableId')) : null,
        })
      }}
    >
      <h3>{title}</h3>
      <label>
        Name
        <input name="name" defaultValue={initial.name ?? ''} required autoComplete="name" />
      </label>
      <label>
        Phone
        <input
          name="phone"
          defaultValue={initial.phone ?? ''}
          required
          inputMode="tel"
          autoComplete="tel"
        />
      </label>
      <label>
        Party size
        <input
          name="partySize"
          type="number"
          min="1"
          max="12"
          defaultValue={initial.partySize ?? 2}
          required
        />
      </label>
      <label>
        Notes
        <input name="notes" defaultValue={initial.notes ?? ''} />
      </label>
      {showReservationFields ? (
        <>
          <label>
            Type
            <select name="source" defaultValue={initial.source ?? 'walk-in'}>
              <option value="walk-in">Walk-in</option>
              <option value="reservation">Reservation</option>
            </select>
          </label>
          <label>
            Reservation time
            <input
              name="reservationTime"
              type="datetime-local"
              defaultValue={initial.reservationTimeLocal ?? ''}
            />
          </label>
          <label>
            Hold table
            <select name="tableId" defaultValue={initial.tableId ?? ''}>
              <option value="">None</option>
              {tables
                .filter((table) => table.status === 'free' || table.id === initial.tableId)
                .map((table) => (
                  <option key={table.id} value={table.id}>
                    {table.name} · {table.seats} seats
                  </option>
                ))}
            </select>
          </label>
        </>
      ) : null}
      <div className="form-actions">
        {onCancel ? (
          <button type="button" className="btn ghost" onClick={onCancel}>
            Cancel
          </button>
        ) : null}
        <button type="submit" className="btn primary">
          {submitLabel}
        </button>
      </div>
    </form>
  )
}
