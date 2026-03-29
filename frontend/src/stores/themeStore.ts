import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark' | 'auto'

interface ThemeState {
  theme: Theme
  setTheme: (theme: Theme) => void
  isDark: boolean
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'auto',
      isDark: false,
      setTheme: (theme: Theme) => {
        set({ theme })
        applyTheme(theme)
      },
    }),
    {
      name: 'theme-storage',
    }
  )
)

function applyTheme(theme: Theme) {
  const root = document.documentElement

  if (theme === 'auto') {
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    root.classList.toggle('dark', isDark)
    useThemeStore.setState({ isDark })
  } else {
    root.classList.toggle('dark', theme === 'dark')
    useThemeStore.setState({ isDark: theme === 'dark' })
  }
}

// 初始化主题
if (typeof window !== 'undefined') {
  const stored = localStorage.getItem('theme-storage')
  const theme = stored ? JSON.parse(stored).state.theme : 'auto'
  applyTheme(theme)

  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const currentTheme = useThemeStore.getState().theme
    if (currentTheme === 'auto') {
      applyTheme('auto')
    }
  })
}
