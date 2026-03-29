import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { authAPI } from '../../services/api'

export function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!email || !password || !confirmPassword) {
      setError('请填写所有字段')
      return
    }
    if (password.length < 6) {
      setError('密码至少6位')
      return
    }
    if (password !== confirmPassword) {
      setError('两次密码不一致')
      return
    }
    setLoading(true)
    try {
      const res = await authAPI.register(email, password)
      setAuth(res.data.access_token, { id: res.data.user_id.toString(), email: res.data.email, nickname: res.data.nickname })
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="card w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🏠</span>
          </div>
          <h1 className="text-h2 text-text-primary font-semibold">注册 LifeButler</h1>
          <p className="text-caption text-text-secondary mt-2">开始你的智能生活</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-text-primary mb-2">邮箱</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field w-full" placeholder="your@email.com" />
          </div>
          <div>
            <label className="block text-sm text-text-primary mb-2">密码</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field w-full" placeholder="至少6位" />
          </div>
          <div>
            <label className="block text-sm text-text-primary mb-2">确认密码</label>
            <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="input-field w-full" placeholder="再次输入密码" />
          </div>
          {error && <p className="text-error text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? '注册中...' : '注册'}</button>
        </form>
        <p className="text-center text-sm text-text-secondary mt-6">
          已有账号? <Link to="/login" className="text-primary hover:underline">立即登录</Link>
        </p>
      </div>
    </div>
  )
}
