import { getJson } from './apiClient'
import { ApiError, type HealthResponse } from '../types/api'

export async function getHealth(): Promise<HealthResponse> {
  const body = await getJson('/health')
  if (!body || typeof body !== 'object' || (body as HealthResponse).status !== 'ok' || (body as HealthResponse).service !== 'gapscope-backend') throw new ApiError('invalid-response', 'The server returned an unexpected health response.')
  return body as HealthResponse
}
