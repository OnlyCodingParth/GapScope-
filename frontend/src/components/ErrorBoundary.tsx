import { Component, type ErrorInfo, type ReactNode } from 'react'

export class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false }
  static getDerivedStateFromError() { return { hasError: true } }
  componentDidCatch(_error: Error, _info: ErrorInfo) {}
  render() { return this.state.hasError ? <main className="error-screen"><h1>Something went wrong</h1><p>Please refresh the page and try again.</p></main> : this.props.children }
}
