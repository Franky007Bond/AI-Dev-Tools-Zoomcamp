import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App.jsx'
import { createApi } from './api/client.js'
import { createMockBackend } from './api/mockBackend.js'

function renderHost() {
  const api = createApi(createMockBackend({ persist: false }))
  render(<App api={api} />)
  return { api }
}

describe('Waitly host UI', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/')
    vi.spyOn(window, 'setInterval').mockReturnValue(1)
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('shows the live queue and floor plan', async () => {
    renderHost()
    expect(await screen.findByRole('heading', { name: 'Waitly Bistro' })).toBeInTheDocument()
    expect(screen.getByText(/Nguyen/)).toBeInTheDocument()
    expect(screen.getByLabelText(/T5, 4 seats, reserved, Okoye/)).toBeInTheDocument()
  })

  it('adds a walk-in from the host form', async () => {
    const user = userEvent.setup()
    renderHost()
    await screen.findByText(/Nguyen/)
    await user.click(screen.getByRole('button', { name: 'Add party' }))
    await user.clear(screen.getByLabelText('Name'))
    await user.type(screen.getByLabelText('Name'), 'Kim')
    await user.clear(screen.getByLabelText('Phone'))
    await user.type(screen.getByLabelText('Phone'), '555-0110')
    await user.click(screen.getByRole('button', { name: 'Add to queue' }))
    expect(await screen.findByText(/Kim/)).toBeInTheDocument()
  })

  it('seats the first party onto a free table', async () => {
    const user = userEvent.setup()
    renderHost()
    await screen.findByText(/Nguyen/)
    await user.selectOptions(screen.getByLabelText('Seat Nguyen'), 't2')
    await waitFor(() => {
      expect(screen.queryByText(/Nguyen · 2/)).not.toBeInTheDocument()
    })
    expect(screen.getByLabelText(/T2, 2 seats, occupied, Nguyen/)).toBeInTheDocument()
  })

  it('simulates a guest SMS confirmation', async () => {
    const user = userEvent.setup()
    renderHost()
    await screen.findByText(/Nguyen/)
    await user.click(screen.getByRole('button', { name: 'SMS' }))
    await user.click(screen.getByRole('button', { name: 'Guest: YES' }))
    await user.click(screen.getByRole('button', { name: 'Board' }))
    expect(await screen.findByText(/On the way/)).toBeInTheDocument()
  })
})

describe('guest join page', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/join')
    vi.spyOn(window, 'setInterval').mockReturnValue(1)
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('lets a guest join the waitlist', async () => {
    const user = userEvent.setup()
    const api = createApi(createMockBackend({ persist: false }))
    render(<App api={api} />)
    await user.type(screen.getByLabelText('Name'), 'Guest')
    await user.type(screen.getByLabelText('Phone'), '555-0123')
    await user.click(screen.getByRole('button', { name: 'Join queue' }))
    expect(await screen.findByText(/You're on the list/)).toBeInTheDocument()
    const snap = await api.getSnapshot()
    expect(snap.queue.some((party) => party.name === 'Guest')).toBe(true)
  })
})
