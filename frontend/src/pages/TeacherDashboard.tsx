import { Badge } from '../components/Badge'
import { EmptyState } from '../components/EmptyState'
import { PageContainer } from '../components/PageContainer'
import { useDocumentTitle } from './useDocumentTitle'

export function TeacherDashboard() { useDocumentTitle('Teacher preview | GapScope'); return <PageContainer><section className="dashboard"><Badge>Foundation preview</Badge><h1>Teacher space</h1><EmptyState title="Your class view is being prepared"><ul><li>See learning patterns across a class.</li><li>Understand evidence behind flagged concepts.</li><li>Plan targeted follow-up support.</li></ul></EmptyState></section></PageContainer> }
