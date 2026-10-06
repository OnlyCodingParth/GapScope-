import { ButtonLink } from '../components/Button'
import { PageContainer } from '../components/PageContainer'
import { useDocumentTitle } from './useDocumentTitle'

export function NotFound() { useDocumentTitle('Page not found | GapScope'); return <PageContainer><section className="centered not-found"><h1>Page not found</h1><p>The page you requested does not exist.</p><ButtonLink to="/">Return home</ButtonLink></section></PageContainer> }
