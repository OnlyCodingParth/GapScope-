import { useEffect, useRef } from 'react'
import { Button } from './Button'

type GoogleResponse = { credential: string }
declare global { interface Window { google?: { accounts: { id: { initialize: (options: { client_id: string; callback: (response: GoogleResponse) => void }) => void; renderButton: (element: HTMLElement, options: object) => void } } } } }

export function GoogleSignInSlot({ onCredential, disabled }: { onCredential: (credential: string) => void; disabled?: boolean }) {
  const target = useRef<HTMLDivElement>(null)
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  useEffect(() => {
    if (!clientId || !target.current) return
    const render = () => { if (window.google && target.current) { window.google.accounts.id.initialize({ client_id: clientId, callback: response => onCredential(response.credential) }); window.google.accounts.id.renderButton(target.current, { theme: 'outline', size: 'large', width: 280, text: 'continue_with' }) } }
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.onload = render
    document.head.appendChild(script)
    return () => script.remove()
  }, [clientId, onCredential])
  if (!clientId) return <div className="google-slot"><Button disabled aria-disabled="true">Continue with Google</Button><p>Google Sign-In is not configured for this environment.</p></div>
  return <div className="google-slot" aria-busy={disabled}><div ref={target} />{disabled && <p>Signing in…</p>}</div>
}
