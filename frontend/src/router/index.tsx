import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from '../components/Layout/AppLayout'
import { LoginPage } from '../components/Auth/LoginPage'
import { RegisterPage } from '../components/Auth/RegisterPage'
import { ChatPage } from '../components/Chat/ChatPage'
import { useAuthStore } from '../stores/authStore'
import { type ReactNode } from 'react'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const token = useAuthStore.getState().token
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

function GuestRoute({ children }: { children: ReactNode }) {
  const token = useAuthStore.getState().token
  if (token) return <Navigate to="/chat" replace />
  return <>{children}</>
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <GuestRoute><LoginPage /></GuestRoute>,
  },
  {
    path: '/register',
    element: <GuestRoute><RegisterPage /></GuestRoute>,
  },
  {
    path: '/',
    element: <ProtectedRoute><AppLayout /></ProtectedRoute>,
    children: [
      { index: true, element: <Navigate to="/chat" replace /> },
      { path: 'chat', element: <ChatPage /> },
      { path: 'calendar', element: <div className="p-8 text-text-primary">日历（开发中）</div> },
      { path: 'settings', element: <div className="p-8 text-text-primary">设置（开发中）</div> },
    ],
  },
])
