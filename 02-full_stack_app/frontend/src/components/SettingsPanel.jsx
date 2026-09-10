export default function SettingsPanel({ settings, onSave, onReset }) {
  const joinUrl =
    typeof window !== 'undefined' ? `${window.location.origin}/join` : '/join'
  const qrSrc = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(joinUrl)}`

  return (
    <section className="panel settings-panel" aria-label="Settings">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Host stand</p>
          <h2>Settings</h2>
        </div>
      </header>

      <form
        className="party-form"
        onSubmit={(event) => {
          event.preventDefault()
          const data = new FormData(event.currentTarget)
          onSave({
            restaurantName: String(data.get('restaurantName')),
            gracePeriodMinutes: Number(data.get('gracePeriodMinutes')),
          })
        }}
      >
        <label>
          Restaurant name
          <input name="restaurantName" defaultValue={settings.restaurantName} required />
        </label>
        <label>
          No-show grace period (minutes)
          <input
            name="gracePeriodMinutes"
            type="number"
            min="1"
            max="30"
            defaultValue={settings.gracePeriodMinutes}
            required
          />
        </label>
        <div className="form-actions">
          <button type="submit" className="btn primary">
            Save settings
          </button>
          <button type="button" className="btn ghost" onClick={onReset}>
            Reset demo data
          </button>
        </div>
      </form>

      <div className="join-card">
        <h3>Guest join link</h3>
        <p>
          Guests scan this QR or open the web form before they arrive. SMS replies stay mocked in
          this build.
        </p>
        <p>
          <a href={joinUrl}>{joinUrl}</a>
        </p>
        <img alt="QR code for the guest join page" src={qrSrc} width="180" height="180" />
      </div>
    </section>
  )
}
