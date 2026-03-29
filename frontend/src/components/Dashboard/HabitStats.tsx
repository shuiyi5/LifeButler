import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { Target, Flame, Award, Inbox } from 'lucide-react'
import { dashboardAPI } from '../../services/api'

interface Habit {
  id: number
  name: string
  streak: number
  total: number
}

const HABIT_ICONS: Record<string, string> = {
  '早起': '🌅', '运动': '💪', '阅读': '📚', '冥想': '🧘', '喝水': '💧',
  '学习': '📖', '写作': '✍️', '跑步': '🏃', '健身': '🏋️', '瑜伽': '🧘‍♀️',
}
const HABIT_COLORS = ['#E8835A', '#7BB6A4', '#F2B84B']

export const HabitStats: FC<{ refreshKey?: number }> = ({ refreshKey }) => {
  const [habits, setHabits] = useState<Habit[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const res = await dashboardAPI.getHabits()
      setHabits(res.data.habits || [])
    } catch {
      setHabits([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData, refreshKey])

  return (
    <div className="bg-surface dark:bg-surface-dark rounded-card shadow-low p-6 lg:col-span-2">
      <h2 className="text-h3 text-text-primary dark:text-text-primary-dark flex items-center gap-2 mb-4">
        <Target size={20} className="text-primary" />
        习惯统计
      </h2>

      {loading ? (
        <div className="flex items-center justify-center h-32 text-text-secondary">加载中...</div>
      ) : habits.length ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {habits.map((habit, idx) => {
            const color = HABIT_COLORS[idx % HABIT_COLORS.length]
            const icon = HABIT_ICONS[habit.name] || '⭐'
            const rate = habit.total > 0 ? Math.round((habit.streak / habit.total) * 100) : 0
            return (
              <div key={habit.id} className="bg-soft dark:bg-background-dark rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">{icon}</span>
                  <span className="text-sm font-medium text-text-primary dark:text-text-primary-dark">{habit.name}</span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <Flame size={16} style={{ color }} />
                  <span className="text-xs text-text-secondary dark:text-text-secondary-dark">连续打卡</span>
                  <span className="ml-auto text-lg font-semibold" style={{ color }}>{habit.streak} 天</span>
                </div>
                <div className="flex items-center gap-2">
                  <Award size={16} className="text-text-secondary dark:text-text-secondary-dark" />
                  <span className="text-xs text-text-secondary dark:text-text-secondary-dark">完成率</span>
                  <span className="ml-auto text-sm font-medium text-text-primary dark:text-text-primary-dark">{rate}%</span>
                </div>
                <div className="mt-3 bg-background dark:bg-surface-dark rounded-full h-2 overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-500" style={{ width: `${rate}%`, backgroundColor: color }} />
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-6 text-text-secondary dark:text-text-secondary-dark">
          <Inbox size={32} className="mb-2 opacity-40" />
          <p className="text-sm">暂无习惯数据</p>
          <p className="text-xs mt-1">在聊天中说「创建一个早起习惯」即可开始打卡</p>
        </div>
      )}
    </div>
  )
}
