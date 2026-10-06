import { apiBaseUrl } from '../lib/config'
import { ApiError } from '../types/api'

export async function getJson(path: string): Promise<unknown> {
  return requestJson(path)
}

export async function requestJson(path: string, options: RequestInit = {}): Promise<unknown> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 8000)
  try {
    const response = await fetch(`${apiBaseUrl}${path}`, { ...options, credentials: 'include', signal: controller.signal, headers: { Accept: 'application/json', ...options.headers } })
    const text = await response.text()
    let body: unknown
    try { body = text ? JSON.parse(text) : null } catch { throw new ApiError('invalid-response', 'The server returned invalid JSON.') }
    if (!response.ok) throw new ApiError('http', `The server returned ${response.status}.`, response.status)
    return body
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (error instanceof DOMException && error.name === 'AbortError') throw new ApiError('timeout', 'The request timed out.')
    throw new ApiError('network', 'The backend is unavailable.')
  } finally { window.clearTimeout(timeout) }
}
