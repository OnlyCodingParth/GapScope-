import { useCallback, useEffect, useState } from 'react'
import { getHealth } from '../services/health'
import { ApiError } from '../types/api'

export type HealthState = 'loading' | 'connected' | 'unavailable' | 'failed' | 'invalid'
export function useHealthCheck() {
  const [state, setState] = useState<HealthState>('loading')
  const check = useCallback(async () => { setState('loading'); try { await getHealth(); setState('connected') } catch (error) { if (error instanceof ApiError) setState(error.kind === 'network' || error.kind === 'timeout' || (error.kind === 'http' && (error.status ?? 0) >= 500) ? 'unavailable' : error.kind === 'invalid-response' ? 'invalid' : 'failed'); else setState('failed') } }, [])
  useEffect(() => { void check() }, [check])
  return { state, retry: check }
}
