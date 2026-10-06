import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { Brand } from './Brand'
import { useAuth } from '../auth/AuthContext'

export function Header() {
  const [open, setOpen] = useState(false)
  const { user, logout } = useAuth()
  return <header className="site-header"><div className="container header-inner"><Brand /><button className="menu-button" aria-expanded={open} aria-controls="site-nav" onClick={() => setOpen(!open)}>Menu</button><nav id="site-nav" className={open ? 'open' : ''} aria-label="Main navigation"><NavLink to="/" onClick={() => setOpen(false)}>Home</NavLink>{user ? <><NavLink to="/student" onClick={() => setOpen(false)}>My quiz</NavLink><button className="nav-action" onClick={() => { void logout(); setOpen(false) }}>Sign out</button></> : <NavLink to="/login" onClick={() => setOpen(false)}>Sign in</NavLink>}</nav></div></header>
}
