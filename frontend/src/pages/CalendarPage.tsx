import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { Calendar, Plus, Trash2, Edit3, MapPin, X, Check } from 'lucide-react'
import { calendarAPI } from '../services/api'

interface Event {
  id: number; title: string; description: string
  start_time: string; end_time: string | null; location: string
}

export const CalendarPage: FC = () => {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [form, setForm] = useState({ title: '', description: '', start_time: '', end_time: '', location: '' })
  const [weekStart, setWeekStart] = useState(() => {
    const d = new Date(); d.setDate(d.getDate() - d.getDay() + 1); d.setHours(0,0,0,0); return d
  })

  const fetchEvents = useCallback(async () => {
    setLoading(true)
    const s = weekStart.toISOString().split('T')[0]
    const e = new Date(weekStart); e.setDate(e.getDate() + 7)
    try {
      const res = await calendarAPI.list(s, e.toISOString().split('T')[0])
      setEvents(res.data)
    } catch { setEvents([]) }
    finally { setLoading(false) }
  }, [weekStart])

  useEffect(() => { fetchEvents() }, [fetchEvents])

  const resetForm = () => { setForm({ title: '', description: '', start_time: '', end_time: '', location: '' }); setEditId(null); setShowForm(false) }

  const handleSave = async () => {
    if (!form.title || !form.start_time) return
    if (editId) { await calendarAPI.update(editId, form) }
    else { await calendarAPI.create(form) }
    resetForm(); fetchEvents()
  }

  const handleEdit = (e: Event) => {
    setForm({ title: e.title, description: e.description, start_time: e.start_time.slice(0,16), end_time: e.end_time?.slice(0,16) || '', location: e.location })
    setEditId(e.id); setShowForm(true)
  }

  const handleDelete = async (id: number) => { await calendarAPI.delete(id); fetchEvents() }

  const prevWeek = () => { const d = new Date(weekStart); d.setDate(d.getDate() - 7); setWeekStart(d) }
  const nextWeek = () => { const d = new Date(weekStart); d.setDate(d.getDate() + 7); setWeekStart(d) }

  const weekDays = Array.from({ length: 7 }, (_, i) => { const d = new Date(weekStart); d.setDate(d.getDate() + i); return d })
  const today = new Date().toDateString()

  const getEventsForDay = (day: Date) => events.filter(e => new Date(e.start_time).toDateString() === day.toDateString())

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 text-text-primary dark:text-text-primary-dark flex items-center gap-2"><Calendar size={28} className="text-primary" />日程管理</h1>
        <button onClick={() => { resetForm(); setShowForm(true) }} className="btn-primary flex items-center gap-1.5 text-sm"><Plus size={16} />新建日程</button>
      </div>

      {/* 周导航 */}
      <div className="flex items-center justify-between mb-4">
        <button onClick={prevWeek} className="px-3 py-1 text-sm rounded-lg bg-soft dark:bg-surface-dark hover:bg-primary-light transition-colors">&lt; 上周</button>
        <span className="text-sm font-medium text-text-primary dark:text-text-primary-dark">
          {weekStart.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })} - {weekDays[6].toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })}
        </span>
        <button onClick={nextWeek} className="px-3 py-1 text-sm rounded-lg bg-soft dark:bg-surface-dark hover:bg-primary-light transition-colors">下周 &gt;</button>
      </div>

      {/* 周视图 */}
      {loading ? <div className="text-center py-20 text-text-secondary">加载中...</div> : (
        <div className="grid grid-cols-7 gap-2">
          {weekDays.map((day) => {
            const isToday = day.toDateString() === today
            const dayEvents = getEventsForDay(day)
            return (
              <div key={day.toISOString()} className={`min-h-[140px] rounded-xl p-2 border transition-colors ${isToday ? 'bg-primary-light/50 dark:bg-primary/10 border-primary/30' : 'bg-surface dark:bg-surface-dark border-border dark:border-border-dark'}`}>
                <p className={`text-xs font-medium mb-1 ${isToday ? 'text-primary' : 'text-text-secondary dark:text-text-secondary-dark'}`}>
                  {day.toLocaleDateString('zh-CN', { weekday: 'short' })} {day.getDate()}
                </p>
                {dayEvents.map((e) => (
                  <div key={e.id} className="group bg-white dark:bg-background-dark rounded-lg px-2 py-1 mb-1 text-xs border border-transparent hover:border-primary/30 cursor-pointer transition-colors" onClick={() => handleEdit(e)}>
                    <p className="font-medium text-text-primary dark:text-text-primary-dark truncate">{e.title}</p>
                    <p className="text-text-secondary dark:text-text-secondary-dark">{new Date(e.start_time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</p>
                    <button onClick={(ev) => { ev.stopPropagation(); handleDelete(e.id) }} className="hidden group-hover:block absolute top-1 right-1 text-error"><Trash2 size={12} /></button>
                  </div>
                ))}
              </div>
            )
          })}
        </div>
      )}

      {/* 弹窗表单 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={resetForm}>
          <div className="bg-surface dark:bg-surface-dark rounded-2xl p-6 w-full max-w-md shadow-high animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-h3 text-text-primary dark:text-text-primary-dark">{editId ? '编辑日程' : '新建日程'}</h3>
              <button onClick={resetForm}><X size={20} className="text-text-secondary" /></button>
            </div>
            <div className="space-y-3">
              <input value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="日程标题" className="input-field w-full" />
              <input type="datetime-local" value={form.start_time} onChange={e => setForm({...form, start_time: e.target.value})} className="input-field w-full" />
              <input type="datetime-local" value={form.end_time} onChange={e => setForm({...form, end_time: e.target.value})} className="input-field w-full" />
              <input value={form.location} onChange={e => setForm({...form, location: e.target.value})} placeholder="地点（可选）" className="input-field w-full" />
              <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="备注（可选）" className="input-field w-full h-20 resize-none" />
            </div>
            <div className="flex gap-2 mt-5">
              <button onClick={resetForm} className="btn-secondary flex-1">取消</button>
              <button onClick={handleSave} className="btn-primary flex-1 flex items-center justify-center gap-1"><Check size={16} />保存</button>
            </div>
            {editId && <button onClick={() => { handleDelete(editId); resetForm() }} className="btn-danger w-full mt-2 flex items-center justify-center gap-1"><Trash2 size={14} />删除此日程</button>}
          </div>
        </div>
      )}
    </div>
  )
}
