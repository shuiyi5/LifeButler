import type { FC } from 'react'
import { useState } from 'react'
import { FinanceChart } from '../components/Dashboard/FinanceChart'
import { HabitCalendar } from '../components/Dashboard/HabitCalendar'
import { HabitStats } from '../components/Dashboard/HabitStats'
import { RefreshCw } from 'lucide-react'

export const DashboardPage: FC = () => {
  const [refreshKey, setRefreshKey] = useState(0)

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 text-text-primary dark:text-text-primary-dark">数据面板</h1>
        <button
          onClick={() => setRefreshKey(k => k + 1)}
          className="flex items-center gap-2 px-3 py-2 text-sm bg-soft dark:bg-surface-dark rounded-lg hover:bg-primary-light dark:hover:bg-primary/10 transition-colors text-text-secondary dark:text-text-secondary-dark hover:text-primary"
        >
          <RefreshCw size={16} />
          刷新
        </button>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FinanceChart refreshKey={refreshKey} />
        <HabitCalendar refreshKey={refreshKey} />
        <HabitStats refreshKey={refreshKey} />
      </div>
    </div>
  )
}
