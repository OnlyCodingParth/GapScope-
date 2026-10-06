import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { ApiError } from '../types/api'
import { requestJson } from '../services/apiClient'

export type AuthUser = { id: string; email: string; name: string; picture: string | null }
type AuthState = { user: AuthUser | null; loading: boolean; error: string | null; signIn: (credential: string) => Promise<boolean>; logout: () => Promise<void> }
const AuthContext = createContext<AuthState | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const refresh = useCallback(async () => {
    try { const body = await requestJson('/auth/me') as { user: AuthUser }; setUser(body.user) }
    catch (reason) { if (!(reason instanceof ApiError) || reason.status !== 401) setError('We could not check your sign-in status.'); setUser(null) }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { void refresh() }, [refresh])
  const signIn = useCallback(async (credential: string) => {
    setError(null)
    try { const body = await requestJson('/auth/google', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ credential }) }) as { user: AuthUser }; setUser(body.user); return true }
    catch { setError('Google sign-in could not be completed. Please try again.'); return false }
  }, [])
  const logout = useCallback(async () => {
    try { await requestJson('/auth/logout', { method: 'POST' }); setUser(null) }
    catch { setError('Sign out could not be completed. Please try again.') }
  }, [])
  return <AuthContext.Provider value={{ user, loading, error, signIn, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() { const value = useContext(AuthContext); if (!value) throw new Error('useAuth must be used within AuthProvider'); return value }
