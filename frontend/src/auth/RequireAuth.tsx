import { Navigate, Outlet } from 'react-router-dom'
import { LoadingState } from '../components/LoadingState'
import { useAuth } from './AuthContext'

export function RequireAuth() { const { user, loading } = useAuth(); if (loading) return <main className="error-screen"><LoadingState /></main>; return user ? <Outlet /> : <Navigate to="/login" replace /> }
