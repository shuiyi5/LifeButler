import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { CheckSquare, Plus, Trash2, X, Check, Circle, CheckCircle2, Clock, AlertCircle } from 'lucide-react'
import { todoAPI } from '../services/api'

interface TodoItem {
  id: number; title: string; description: string
  priority: string; status: string; category: string
  due_date: string | null; created_at: string | null
}

const PRIORITY_MAP: Record<string, { label: string; color: string; icon: typeof AlertCircle }> = {
  high: { label: '高', color: 'text-red-500', icon: AlertCircle },
  medium: { label: '中', color: 'text-accent', icon: Clock },
  low: { label: '低', color: 'text-secondary', icon: Circle },
}

const STATUS_TABS = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待处理' },
  { value: 'in_progress', label: '进行中' },
  { value: 'done', label: '已完成' },
]

export const TodoPage: FC = () => {
  const [todos, setTodos] = useState<TodoItem[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [form, setForm] = useState({ title: '', description: '', priority: 'medium', category: '', due_date: '' })

  const fetchTodos = useCallback(async () => {
    setLoading(true)
    try {
      const res = await todoAPI.list(filter || undefined)
      setTodos(res.data)
    } catch { setTodos([]) }
    finally { setLoading(false) }
  }, [filter])

  useEffect(() => { fetchTodos() }, [fetchTodos])

  const resetForm = () => { setForm({ title: '', description: '', priority: 'medium', category: '', due_date: '' }); setEditId(null); setShowForm(false) }

  const handleSave = async () => {
    if (!form.title) return
    if (editId) { await todoAPI.update(editId, form) }
    else { await todoAPI.create(form) }
    resetForm(); fetchTodos()
  }

  const handleEdit = (t: TodoItem) => {
    setForm({ title: t.title, description: t.description, priority: t.priority, category: t.category, due_date: t.due_date || '' })
    setEditId(t.id); setShowForm(true)
  }

  const handleToggle = async (t: TodoItem) => {
    const next = t.status === 'done' ? 'pending' : 'done'
    await todoAPI.update(t.id, { status: next })
    fetchTodos()
  }

  const handleDelete = async (id: number) => { await todoAPI.delete(id); fetchTodos() }

  const counts = { all: todos.length, pending: todos.filter(t => t.status === 'pending').length, in_progress: todos.filter(t => t.status === 'in_progress').length, done: todos.filter(t => t.status === 'done').length }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 text-text-primary dark:text-text-primary-dark flex items-center gap-2"><CheckSquare size={28} className="text-primary" />待办管理</h1>
        <button onClick={() => { resetForm(); setShowForm(true) }} className="btn-primary flex items-center gap-1.5 text-sm"><Plus size={16} />新建待办</button>
      </div>

      {/* 状态筛选 */}
      <div className="flex gap-2 mb-5">
        {STATUS_TABS.map(tab => (
          <button key={tab.value} onClick={() => setFilter(tab.value)}
            className={`px-4 py-1.5 text-sm rounded-full transition-colors ${filter === tab.value ? 'bg-primary text-white' : 'bg-soft dark:bg-surface-dark text-text-secondary dark:text-text-secondary-dark hover:text-primary'}`}>
            {tab.label} {tab.value === '' ? counts.all : counts[tab.value as keyof typeof counts] || 0}
          </button>
        ))}
      </div>

      {/* 列表 */}
      {loading ? <div className="text-center py-20 text-text-secondary">加载中...</div> : todos.length === 0 ? (
        <div className="text-center py-20 text-text-secondary dark:text-text-secondary-dark">
          <CheckSquare size={48} className="mx-auto mb-3 opacity-30" />
          <p>暂无待办事项</p>
          <p className="text-xs mt-1">点击右上角「新建待办」或在聊天中说「添加待办：买菜」</p>
        </div>
      ) : (
        <div className="space-y-2">
          {todos.map(t => {
            const p = PRIORITY_MAP[t.priority] || PRIORITY_MAP.medium
            const isDone = t.status === 'done'
            return (
              <div key={t.id} className={`flex items-center gap-3 bg-surface dark:bg-surface-dark rounded-xl px-4 py-3 border border-border dark:border-border-dark hover:shadow-low transition-all group ${isDone ? 'opacity-60' : ''}`}>
                <button onClick={() => handleToggle(t)} className="flex-shrink-0">
                  {isDone ? <CheckCircle2 size={22} className="text-secondary" /> : <Circle size={22} className="text-text-secondary/40 hover:text-primary transition-colors" />}
                </button>
                <div className="flex-1 min-w-0 cursor-pointer" onClick={() => handleEdit(t)}>
                  <p className={`text-sm font-medium ${isDone ? 'line-through text-text-secondary' : 'text-text-primary dark:text-text-primary-dark'}`}>{t.title}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={`text-xs ${p.color}`}>{p.label}优先</span>
                    {t.category && <span className="text-xs bg-soft dark:bg-background-dark px-1.5 py-0.5 rounded">{t.category}</span>}
                    {t.due_date && <span className="text-xs text-text-secondary">{t.due_date}</span>}
                  </div>
                </div>
                <button onClick={() => handleDelete(t.id)} className="opacity-0 group-hover:opacity-100 transition-opacity text-text-secondary hover:text-error"><Trash2 size={16} /></button>
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
              <h3 className="text-h3 text-text-primary dark:text-text-primary-dark">{editId ? '编辑待办' : '新建待办'}</h3>
              <button onClick={resetForm}><X size={20} className="text-text-secondary" /></button>
            </div>
            <div className="space-y-3">
              <input value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="待办标题" className="input-field w-full" />
              <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="描述（可选）" className="input-field w-full h-20 resize-none" />
              <div className="flex gap-2">
                {(['high','medium','low'] as const).map(p => (
                  <button key={p} onClick={() => setForm({...form, priority: p})}
                    className={`flex-1 py-2 text-sm rounded-lg border transition-colors ${form.priority === p ? 'border-primary bg-primary-light dark:bg-primary/10 text-primary' : 'border-border dark:border-border-dark text-text-secondary'}`}>
                    {PRIORITY_MAP[p].label}优先
                  </button>
                ))}
              </div>
              <input value={form.category} onChange={e => setForm({...form, category: e.target.value})} placeholder="分类（可选）" className="input-field w-full" />
              <input type="date" value={form.due_date} onChange={e => setForm({...form, due_date: e.target.value})} className="input-field w-full" />
            </div>
            <div className="flex gap-2 mt-5">
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
