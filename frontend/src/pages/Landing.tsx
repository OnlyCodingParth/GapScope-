import { Badge } from '../components/Badge'
import { ButtonLink } from '../components/Button'
import { Card } from '../components/Card'
import { PageContainer } from '../components/PageContainer'
import { useDocumentTitle } from './useDocumentTitle'

export function Landing() { useDocumentTitle('GapScope | Understand the why'); return <PageContainer><section className="hero"><div className="reveal"><Badge>Quadratic equations · coming next</Badge><h1>Don’t just tell students they’re wrong.<br />Tell them why, with evidence.</h1></div><p className="reveal delay-one">GapScope is an education tool being built to turn mistakes into a clearer next step.</p><div className="reveal delay-two"><ButtonLink to="/login">Get started</ButtonLink></div></section><section className="purpose" aria-labelledby="purpose-title"><h2 id="purpose-title">What it is built to do</h2><ul><li>Identify the learning gap behind a mistake.</li><li>Explain why a concept was flagged, with evidence.</li><li>Recommend what to study next.</li><li>Provide targeted practice.</li></ul><Card><strong>Illustration of the planned report, not live output</strong><p>A future report will connect a response to a concept and a focused next step.</p></Card></section><p className="foundation-note">Foundation release: diagnosis and practice are not live yet.</p></PageContainer> }
