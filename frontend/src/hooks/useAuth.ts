import { useAuthStore } from '../stores/authStore'

export const useAuth = () => {
  const { token, user, isAuthenticated, setAuth, logout } = useAuthStore()
  return { token, user, isAuthenticated, login: setAuth, logout }
}
