import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Card } from '../components/Card'
import { ErrorState } from '../components/ErrorState'
import { GoogleSignInSlot } from '../components/GoogleSignInSlot'
import { LoadingState } from '../components/LoadingState'
import { PageContainer } from '../components/PageContainer'
import { useDocumentTitle } from './useDocumentTitle'

export function Login() {
  useDocumentTitle('Sign in | GapScope')
  const { user, loading, error, signIn } = useAuth()
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  if (loading) return <main className="error-screen"><LoadingState /></main>
  if (user) return <Navigate to="/student" replace />
  async function handleCredential(credential: string) { setSubmitting(true); if (await signIn(credential)) navigate('/student'); setSubmitting(false) }
  return <PageContainer><div className="centered"><Card><h1>Welcome to GapScope</h1><p>Sign in to take the Quadratic Equations quiz and keep your own results.</p><GoogleSignInSlot onCredential={handleCredential} disabled={submitting} />{error && <ErrorState message={error} />}</Card></div></PageContainer>
}
