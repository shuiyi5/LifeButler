import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { BookOpen, Plus, Trash2, X, Check } from 'lucide-react'
import { readingAPI } from '../services/api'

interface Plan { id: number; book_title: string; author: string; total_pages: number; current_page: number; status: string; target_date: string | null }

export const ReadingPage: FC = () => {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [form, setForm] = useState({ book_title: '', author: '', total_pages: 300, current_page: 0, target_date: '' })

  const fetch = useCallback(async () => {
    setLoading(true)
    try { const r = await readingAPI.list(); setPlans(r.data) } catch { setPlans([]) }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { fetch() }, [fetch])

  const resetForm = () => { setForm({ book_title: '', author: '', total_pages: 300, current_page: 0, target_date: '' }); setEditId(null); setShowForm(false) }

  const handleSave = async () => {
    if (!form.book_title) return
    if (editId) { await readingAPI.update(editId, form) } else { await readingAPI.create(form) }
    resetForm(); fetch()
  }
  const handleEdit = (p: Plan) => { setForm({ book_title: p.book_title, author: p.author, total_pages: p.total_pages, current_page: p.current_page, target_date: p.target_date || '' }); setEditId(p.id); setShowForm(true) }
  const handleDelete = async (id: number) => { await readingAPI.delete(id); resetForm(); fetch() }

  const reading = plans.filter(p => p.status === 'reading')
  const completed = plans.filter(p => p.status === 'completed')
  const totalPages = plans.reduce((s, p) => s + p.current_page, 0)

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 text-text-primary dark:text-text-primary-dark flex items-center gap-2"><BookOpen size={28} className="text-primary" />读书学习</h1>
        <button onClick={() => { resetForm(); setShowForm(true) }} className="btn-primary flex items-center gap-1.5 text-sm"><Plus size={16} />新计划</button>
      </div>
      {/* 统计 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-primary-light/50 dark:bg-primary/10 rounded-xl p-4 text-center"><p className="text-2xl font-bold text-primary">{reading.length}</p><p className="text-xs text-text-secondary">在读</p></div>
        <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 text-center"><p className="text-2xl font-bold text-green-600">{completed.length}</p><p className="text-xs text-text-secondary">已读完</p></div>
        <div className="bg-soft dark:bg-surface-dark rounded-xl p-4 text-center"><p className="text-2xl font-bold text-text-primary dark:text-text-primary-dark">{totalPages}</p><p className="text-xs text-text-secondary">累计页数</p></div>
      </div>
      {loading ? <div className="text-center py-20 text-text-secondary">加载中...</div> : plans.length === 0 ? (
        <div className="text-center py-20 text-text-secondary"><BookOpen size={48} className="mx-auto mb-3 opacity-30" /><p>暂无读书计划</p><p className="text-xs mt-1">点击「新计划」或聊天中说「开始读《原则》300页」</p></div>
      ) : (
        <div className="space-y-3">
          {plans.map(p => {
            const pct = p.total_pages > 0 ? Math.round(p.current_page / p.total_pages * 100) : 0
            return (
              <div key={p.id} onClick={() => handleEdit(p)} className="bg-surface dark:bg-surface-dark rounded-xl p-4 border border-border dark:border-border-dark hover:shadow-low cursor-pointer group transition-all">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="text-sm font-medium text-text-primary dark:text-text-primary-dark">《{p.book_title}》</h3>
                    {p.author && <p className="text-xs text-text-secondary">{p.author}</p>}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 text-xs rounded-full ${p.status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-primary-light text-primary'}`}>{p.status === 'completed' ? '已读完' : '阅读中'}</span>
                    <button onClick={e => { e.stopPropagation(); handleDelete(p.id) }} className="opacity-0 group-hover:opacity-100 text-text-secondary hover:text-error"><Trash2 size={14} /></button>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-soft dark:bg-background-dark rounded-full h-2 overflow-hidden">
                    <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-xs text-text-secondary w-20 text-right">{p.current_page}/{p.total_pages}页</span>
                </div>
              </div>
            )
          })}
        </div>
      )}
      {showForm && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={resetForm}>
          <div className="bg-surface dark:bg-surface-dark rounded-2xl p-6 w-full max-w-md shadow-high animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-h3 text-text-primary dark:text-text-primary-dark">{editId ? '更新进度' : '新读书计划'}</h3>
              <button onClick={resetForm}><X size={20} className="text-text-secondary" /></button>
            </div>
            <div className="space-y-3">
              <input value={form.book_title} onChange={e => setForm({...form, book_title: e.target.value})} placeholder="书名" className="input-field w-full" />
              <input value={form.author} onChange={e => setForm({...form, author: e.target.value})} placeholder="作者（可选）" className="input-field w-full" />
              <div className="flex gap-2">
                <div className="flex-1"><label className="text-xs text-text-secondary mb-1 block">总页数</label><input type="number" value={form.total_pages} onChange={e => setForm({...form, total_pages: Number(e.target.value)})} className="input-field w-full" /></div>
                <div className="flex-1"><label className="text-xs text-text-secondary mb-1 block">当前页</label><input type="number" value={form.current_page} onChange={e => setForm({...form, current_page: Number(e.target.value)})} className="input-field w-full" /></div>
              </div>
              <input type="date" value={form.target_date} onChange={e => setForm({...form, target_date: e.target.value})} className="input-field w-full" />
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={resetForm} className="btn-secondary flex-1">取消</button>
              <button onClick={handleSave} className="btn-primary flex-1 flex items-center justify-center gap-1"><Check size={16} />保存</button>
            </div>
            {editId && <button onClick={() => { handleDelete(editId); resetForm() }} className="btn-danger w-full mt-2 flex items-center justify-center gap-1"><Trash2 size={14} />删除</button>}
          </div>
        </div>
      )}
    </div>
  )
}
