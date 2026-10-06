import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { ErrorBoundary } from './components/ErrorBoundary'
import { AppLayout } from './layouts/AppLayout'
import { Landing } from './pages/Landing'
import { Login } from './pages/Login'
import { NotFound } from './pages/NotFound'
import { RouteError } from './pages/RouteError'
import { StudentDashboard } from './pages/StudentDashboard'
import { TeacherDashboard } from './pages/TeacherDashboard'
import { AuthProvider } from './auth/AuthContext'
import { RequireAuth } from './auth/RequireAuth'

const router = createBrowserRouter([{ path: '/', element: <AppLayout />, errorElement: <RouteError />, children: [{ index: true, element: <Landing /> }, { path: 'login', element: <Login /> }, { element: <RequireAuth />, children: [{ path: 'student', element: <StudentDashboard /> }] }, { path: 'teacher', element: <TeacherDashboard /> }, { path: '*', element: <NotFound /> }] }])
export default function App() { return <ErrorBoundary><AuthProvider><RouterProvider router={router} /></AuthProvider></ErrorBoundary> }
