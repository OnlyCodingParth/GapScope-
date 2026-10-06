import { Outlet } from 'react-router-dom'
import { Header } from '../components/Header'
import { PageContainer } from '../components/PageContainer'
import { StatusIndicator } from '../components/StatusIndicator'

export function AppLayout() { return <><a className="skip-link" href="#main-content">Skip to content</a><Header /><main id="main-content"><Outlet /></main><footer><PageContainer><div className="footer-inner"><p>GapScope · foundation release</p><StatusIndicator /></div></PageContainer></footer></> }
