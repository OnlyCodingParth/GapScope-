import { useHealthCheck } from '../lib/useHealthCheck'
import { ErrorState } from './ErrorState'
import { LoadingState } from './LoadingState'

export function StatusIndicator() {
  const { state, retry } = useHealthCheck()
  if (state === 'loading') return <div aria-live="polite"><LoadingState /></div>
  if (state === 'connected') return <p className="status connected" aria-live="polite"><span />Backend connected</p>
  const message = state === 'unavailable' ? 'Backend unavailable.' : state === 'invalid' ? 'Backend returned an unexpected response.' : 'Backend request failed.'
  return <div aria-live="polite"><p className="status unavailable"><span />{message}</p><ErrorState message="You can retry after the backend is running." retry={retry} /></div>
}
