import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { Calendar, ChevronLeft, ChevronRight, Inbox } from 'lucide-react'
import { dashboardAPI } from '../../services/api'

export const HabitCalendar: FC<{ refreshKey?: number }> = ({ refreshKey }) => {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [checkedDays, setCheckedDays] = useState<Set<number>>(new Set())
  const [habits, setHabits] = useState<{ id: number; name: string }[]>([])
  const [selectedHabitId, setSelectedHabitId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstDayOfWeek = new Date(year, month, 1).getDay()
  const monthName = currentDate.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })

  // 加载习惯列表
  const fetchHabits = useCallback(async () => {
    try {
      const res = await dashboardAPI.getHabits()
      const list = res.data.habits || []
      setHabits(list)
      if (list.length > 0 && selectedHabitId === null) {
        setSelectedHabitId(list[0].id)
      }
    } catch {
      setHabits([])
    }
  }, [selectedHabitId])

  useEffect(() => { fetchHabits() }, [fetchHabits, refreshKey])

  // 加载打卡日历
  const fetchCalendar = useCallback(async () => {
    if (!selectedHabitId) { setLoading(false); return }
    setLoading(true)
    try {
      const res = await dashboardAPI.getHabitCalendar(selectedHabitId, year, month + 1)
      setCheckedDays(new Set(res.data.checked_days || []))
    } catch {
      setCheckedDays(new Set())
    } finally {
      setLoading(false)
    }
  }, [selectedHabitId, year, month])

  useEffect(() => { fetchCalendar() }, [fetchCalendar, refreshKey])

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1))
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1))

  const days: (number | null)[] = []
  for (let i = 0; i < firstDayOfWeek; i++) days.push(null)
  for (let i = 1; i <= daysInMonth; i++) days.push(i)

  const today = new Date()
  const isCurrentMonth = today.getFullYear() === year && today.getMonth() === month

  return (
    <div className="bg-surface dark:bg-surface-dark rounded-card shadow-low p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-h3 text-text-primary dark:text-text-primary-dark flex items-center gap-2">
          <Calendar size={20} className="text-primary" />
          打卡日历
        </h2>
        <div className="flex items-center gap-2">
          <button onClick={prevMonth} className="p-1 rounded-lg hover:bg-soft dark:hover:bg-background-dark transition-colors">
            <ChevronLeft size={18} className="text-text-secondary" />
          </button>
          <span className="text-sm text-text-primary dark:text-text-primary-dark font-medium min-w-[100px] text-center">{monthName}</span>
          <button onClick={nextMonth} className="p-1 rounded-lg hover:bg-soft dark:hover:bg-background-dark transition-colors">
            <ChevronRight size={18} className="text-text-secondary" />
          </button>
        </div>
      </div>

      {/* 习惯选择器 */}
      {habits.length > 1 && (
        <div className="flex gap-1 mb-4 overflow-x-auto">
          {habits.map((h) => (
            <button
              key={h.id}
              onClick={() => setSelectedHabitId(h.id)}
              className={`px-3 py-1 text-xs rounded-full whitespace-nowrap transition-colors ${
                selectedHabitId === h.id
                  ? 'bg-primary text-white'
                  : 'bg-soft dark:bg-background-dark text-text-secondary dark:text-text-secondary-dark'
              }`}
            >
              {h.name}
            </button>
          ))}
        </div>
      )}

      {habits.length === 0 && !loading ? (
        <div className="flex flex-col items-center justify-center py-10 text-text-secondary dark:text-text-secondary-dark">
          <Inbox size={32} className="mb-2 opacity-40" />
          <p className="text-sm">暂无习惯</p>
          <p className="text-xs mt-1">在聊天中说「创建一个运动习惯」开始打卡</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-7 gap-1 mb-2">
            {['日', '一', '二', '三', '四', '五', '六'].map((d) => (
              <div key={d} className="text-center text-xs text-text-secondary dark:text-text-secondary-dark py-1">{d}</div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-1">
            {days.map((day, idx) => {
              if (day === null) return <div key={`empty-${idx}`} />
              const isChecked = checkedDays.has(day)
              const isToday = isCurrentMonth && day === today.getDate()
              return (
                <div
                  key={day}
                  className={`aspect-square flex items-center justify-center rounded-lg text-sm transition-colors ${
                    isChecked
                      ? 'bg-primary text-white'
                      : isToday
                        ? 'bg-primary/10 text-primary font-semibold'
                        : 'text-text-primary dark:text-text-primary-dark hover:bg-soft dark:hover:bg-background-dark'
                  }`}
                >
                  {day}
                </div>
              )
            })}
          </div>

          <div className="flex items-center gap-4 mt-4 text-xs text-text-secondary dark:text-text-secondary-dark">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded bg-primary" /> 已打卡
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded bg-primary/10 border border-primary/30" /> 今天
            </div>
            <span className="ml-auto">本月 {checkedDays.size}/{daysInMonth} 天</span>
          </div>
        </>
      )}
    </div>
  )
}
