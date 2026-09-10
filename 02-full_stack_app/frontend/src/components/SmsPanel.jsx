import { formatTime } from '../format.js'

export default function SmsPanel({ sms, parties, onReply }) {
  const waiting = parties.filter((party) =>
    ['waiting', 'notified', 'confirmed'].includes(party.status),
  )

  return (
    <section className="panel sms-panel" aria-label="SMS inbox">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Two-way SMS</p>
          <h2>Guest texts</h2>
        </div>
      </header>
      <p className="hint">
        Outbound texts are mocked. Use the guest replies to confirm or cancel as if a phone answered.
      </p>

      <div className="reply-row">
        {waiting
          .filter((party) => party.status === 'notified')
          .map((party) => (
            <article key={party.id} className="reply-card">
              <strong>{party.name}</strong>
              <span>was told their table is ready</span>
              <div className="form-actions">
                <button type="button" className="btn primary" onClick={() => onReply(party.id, 'YES')}>
                  Guest: YES
                </button>
                <button type="button" className="btn danger" onClick={() => onReply(party.id, 'CANCEL')}>
                  Guest: CANCEL
                </button>
              </div>
            </article>
          ))}
      </div>

      <ol className="sms-list">
        {sms.map((message) => {
          const party = parties.find((item) => item.id === message.partyId)
          return (
            <li key={message.id} className={`sms ${message.direction}`}>
              <div>
                <strong>{party?.name ?? 'Guest'}</strong>
                <span>{formatTime(message.at)}</span>
              </div>
              <p>{message.body}</p>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
