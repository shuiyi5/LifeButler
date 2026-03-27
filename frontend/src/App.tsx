import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'

// 页面占位（后续实现）
const LoginPage = () => <div>登录页面</div>
const RegisterPage = () => <div>注册页面</div>
const HomePage = () => <div>首页</div>
const ChatPage = () => <div>对话页面</div>
const DashboardPage = () => <div>数据面板</div>
const SettingsPage = () => <div>设置页面</div>

// 路由守卫
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
