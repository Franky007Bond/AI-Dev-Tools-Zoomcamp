import { useState } from 'react'
import PartyForm from '../components/PartyForm.jsx'

export default function GuestJoin({ api }) {
  const [done, setDone] = useState(null)
  const [error, setError] = useState('')

  if (done) {
    return (
      <main className="guest-page">
        <section className="guest-card">
          <p className="eyebrow">Waitly</p>
          <h1>You're on the list</h1>
          <p>
            {done.name}, party of {done.partySize}. We'll text {done.phone} with updates.
            {done.waitEstimateMinutes != null
              ? ` Estimated wait is ${done.waitEstimateMinutes} minutes.`
              : ''}
          </p>
        </section>
      </main>
    )
  }

  return (
    <main className="guest-page">
      <section className="guest-card">
        <p className="eyebrow">Waitly</p>
        <h1>Join the waitlist</h1>
        <p>No account needed. We'll text you when your table is ready.</p>
        {error ? <p className="banner error">{error}</p> : null}
        <PartyForm
          title="Your party"
          submitLabel="Join queue"
          onSubmit={async (input) => {
            try {
              setError('')
              const snapshot = await api.addParty({ ...input, source: 'remote' })
              const created = snapshot.queue.find((party) => party.phone === input.phone)
              setDone(created ?? { ...input, waitEstimateMinutes: null })
            } catch (err) {
              setError(err.message ?? 'Could not join')
            }
          }}
        />
      </section>
    </main>
  )
}
