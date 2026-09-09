import HostStand from './pages/HostStand.jsx'
import GuestJoin from './pages/GuestJoin.jsx'
import { api as defaultApi } from './api/client.js'

export default function App({ api = defaultApi }) {
  const path = window.location.pathname
  if (path.startsWith('/join')) {
    return <GuestJoin api={api} />
  }
  return <HostStand api={api} />
}
