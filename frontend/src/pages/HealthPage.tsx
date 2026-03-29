import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { Apple, Plus, Trash2, Droplet } from 'lucide-react'
import { healthAPI } from '../services/api'

interface Record { id: number; meal_type: string; food_items: string[]; calories_estimate: number; water_ml: number; date: string }

const MEAL_TYPES = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '加餐', water: '饮水' }

export const HealthPage: FC = () => {
  const [records, setRecords] = useState<Record[]>([])
  const [loading, setLoading] = useState(true)
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ meal_type: 'lunch', food_items: '', calories_estimate: 0, water_ml: 0 })

  const fetch = useCallback(async () => {
    setLoading(true)
    try { const r = await healthAPI.list(date); setRecords(r.data) } catch { setRecords([]) }
    finally { setLoading(false) }
  }, [date])
  useEffect(() => { fetch() }, [fetch])

  const totalCal = records.filter(r => r.meal_type !== 'water').reduce((s, r) => s + r.calories_estimate, 0)
  const totalWater = records.reduce((s, r) => s + r.water_ml, 0)
  const mealCount = records.filter(r => r.meal_type !== 'water').length

  const handleAdd = async () => {
    const foods = form.food_items.split(',').map(f => f.trim()).filter(Boolean)
    await healthAPI.create({ ...form, food_items: foods, date })
    setForm({ meal_type: 'lunch', food_items: '', calories_estimate: 0, water_ml: 0 }); setShowForm(false); fetch()
  }
  const handleDelete = async (id: number) => { await healthAPI.delete(id); fetch() }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 text-text-primary dark:text-text-primary-dark flex items-center gap-2"><Apple size={28} className="text-primary" />饮食健康</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-1.5 text-sm"><Plus size={16} />记录</button>
      </div>
      <div className="flex items-center gap-2 mb-6">
        <input type="date" value={date} onChange={e => setDate(e.target.value)} className="input-field" />
        <button onClick={() => setDate(new Date().toISOString().split('T')[0])} className="px-3 py-1.5 text-xs rounded-lg bg-soft hover:bg-primary-light transition-colors">今天</button>
      </div>
      {/* 统计 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-4 text-center"><p className="text-2xl font-bold text-red-600">{totalCal}</p><p className="text-xs text-text-secondary">千卡</p></div>
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 text-center"><p className="text-2xl font-bold text-blue-600">{totalWater}</p><p className="text-xs text-text-secondary">ml饮水</p></div>
        <div className="bg-soft dark:bg-surface-dark rounded-xl p-4 text-center"><p className="text-2xl font-bold text-text-primary dark:text-text-primary-dark">{mealCount}</p><p className="text-xs text-text-secondary">餐</p></div>
      </div>
      {loading ? <div className="text-center py-20 text-text-secondary">加载中...</div> : records.length === 0 ? (
        <div className="text-center py-20 text-text-secondary"><Apple size={48} className="mx-auto mb-3 opacity-30" /><p>今日暂无记录</p><p className="text-xs mt-1">点击「记录」或聊天中说「中午吃了牛肉面」</p></div>
      ) : (
        <div className="space-y-2">
          {records.map(r => (
            <div key={r.id} className="flex items-center gap-3 bg-surface dark:bg-surface-dark rounded-xl px-4 py-3 border border-border dark:border-border-dark group">
              <div className="w-10 h-10 rounded-full bg-primary-light dark:bg-primary/10 flex items-center justify-center flex-shrink-0">
                {r.meal_type === 'water' ? <Droplet size={18} className="text-primary" /> : <Apple size={18} className="text-primary" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary dark:text-text-primary-dark">{MEAL_TYPES[r.meal_type as keyof typeof MEAL_TYPES] || r.meal_type}</p>
                {r.food_items.length > 0 && <p className="text-xs text-text-secondary">{r.food_items.join(', ')}</p>}
              </div>
              {r.meal_type === 'water' ? (
                <span className="text-sm text-blue-600">{r.water_ml}ml</span>
              ) : (
                <span className="text-sm text-red-600">~{r.calories_estimate}千卡</span>
              )}
              <button onClick={() => handleDelete(r.id)} className="opacity-0 group-hover:opacity-100 text-text-secondary hover:text-error"><Trash2 size={14} /></button>
            </div>
          ))}
        </div>
      )}
      {showForm && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={() => setShowForm(false)}>
          <div className="bg-surface dark:bg-surface-dark rounded-2xl p-6 w-full max-w-sm shadow-high animate-scale-in" onClick={e => e.stopPropagation()}>
            <h3 className="text-h3 text-text-primary dark:text-text-primary-dark mb-4">记录饮食</h3>
            <div className="space-y-3">
              <div className="flex gap-1 flex-wrap">{Object.entries(MEAL_TYPES).map(([k, v]) => <button key={k} onClick={() => setForm({...form, meal_type: k})} className={`px-3 py-1 text-xs rounded-full ${form.meal_type === k ? 'bg-primary text-white' : 'bg-soft text-text-secondary'}`}>{v}</button>)}</div>
              {form.meal_type === 'water' ? (
                <input type="number" value={form.water_ml} onChange={e => setForm({...form, water_ml: Number(e.target.value)})} placeholder="饮水量(ml)" className="input-field w-full" />
              ) : (
                <>
                  <input value={form.food_items} onChange={e => setForm({...form, food_items: e.target.value})} placeholder="食物（逗号分隔）" className="input-field w-full" />
                  <input type="number" value={form.calories_estimate} onChange={e => setForm({...form, calories_estimate: Number(e.target.value)})} placeholder="预估热量(千卡)" className="input-field w-full" />
                </>
              )}
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setShowForm(false)} className="btn-secondary flex-1">取消</button>
              <button onClick={handleAdd} className="btn-primary flex-1">添加</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
