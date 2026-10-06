const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()
export const apiBaseUrl = configuredBaseUrl || '/api'
