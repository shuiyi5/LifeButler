import { create } from 'zustand'

interface DashboardState {
  overview: any
  setOverview: (data: any) => void
}

export const useDashboardStore = create<DashboardState>((set) => ({
  overview: null,
  setOverview: (data) => set({ overview: data }),
}))
