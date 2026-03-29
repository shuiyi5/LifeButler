import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { StickyNote, Plus, Trash2, X, Check, Search } from 'lucide-react'
import { notesAPI } from '../services/api'

interface NoteItem { id: number; title: string; content: string; updated_at: string | null }

export const NotesPage: FC = () => {
  const [notes, setNotes] = useState<NoteItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<NoteItem | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', content: '' })
  const [editId, setEditId] = useState<number | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try { const r = await notesAPI.list(); setNotes(r.data) } catch { setNotes([]) }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { fetch() }, [fetch])

  const filtered = notes.filter(n => !search || n.title.includes(search) || n.content.includes(search))

  const handleSave = async () => {
    if (!form.title && !form.content) return
    if (!form.title) form.title = form.content.slice(0, 20) || '新笔记'
    if (editId) { await notesAPI.update(editId, form) } else { await notesAPI.create(form) }
    setForm({ title: '', content: '' }); setEditId(null); setShowForm(false); setSelected(null); fetch()
  }
  const handleEdit = (n: NoteItem) => { setForm({ title: n.title, content: n.content }); setEditId(n.id); setShowForm(true) }
  const handleDelete = async (id: number) => { await notesAPI.delete(id); if (selected?.id === id) setSelected(null); fetch() }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 text-text-primary dark:text-text-primary-dark flex items-center gap-2"><StickyNote size={28} className="text-primary" />备忘笔记</h1>
        <button onClick={() => { setForm({ title: '', content: '' }); setEditId(null); setShowForm(true) }} className="btn-primary flex items-center gap-1.5 text-sm"><Plus size={16} />新建</button>
      </div>
      <div className="relative mb-4">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="搜索笔记..." className="input-field w-full pl-9" />
      </div>
      {loading ? <div className="text-center py-20 text-text-secondary">加载中...</div> : filtered.length === 0 ? (
        <div className="text-center py-20 text-text-secondary"><StickyNote size={48} className="mx-auto mb-3 opacity-30" /><p>暂无笔记</p><p className="text-xs mt-1">点击「新建」或聊天中说「记一下：...」</p></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filtered.map(n => (
            <div key={n.id} onClick={() => handleEdit(n)} className="bg-surface dark:bg-surface-dark rounded-xl p-4 border border-border dark:border-border-dark hover:shadow-low transition-all cursor-pointer group">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-medium text-text-primary dark:text-text-primary-dark truncate flex-1">{n.title}</h3>
                <button onClick={e => { e.stopPropagation(); handleDelete(n.id) }} className="opacity-0 group-hover:opacity-100 text-text-secondary hover:text-error"><Trash2 size={14} /></button>
              </div>
              <p className="text-xs text-text-secondary dark:text-text-secondary-dark line-clamp-3">{n.content}</p>
              {n.updated_at && <p className="text-[10px] text-text-secondary/50 mt-2">{new Date(n.updated_at).toLocaleDateString('zh-CN')}</p>}
            </div>
          ))}
        </div>
      )}
      {showForm && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={() => setShowForm(false)}>
          <div className="bg-surface dark:bg-surface-dark rounded-2xl p-6 w-full max-w-lg shadow-high animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-h3 text-text-primary dark:text-text-primary-dark">{editId ? '编辑笔记' : '新建笔记'}</h3>
              <button onClick={() => setShowForm(false)}><X size={20} className="text-text-secondary" /></button>
            </div>
            <div className="space-y-3">
              <input value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="标题（可选）" className="input-field w-full" />
              <textarea value={form.content} onChange={e => setForm({...form, content: e.target.value})} placeholder="写点什么..." className="input-field w-full h-48 resize-none" />
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={() => setShowForm(false)} className="btn-secondary flex-1">取消</button>
              <button onClick={handleSave} className="btn-primary flex-1 flex items-center justify-center gap-1"><Check size={16} />保存</button>
            </div>
            {editId && <button onClick={() => { handleDelete(editId); setShowForm(false) }} className="btn-danger w-full mt-2 flex items-center justify-center gap-1"><Trash2 size={14} />删除</button>}
          </div>
        </div>
      )}
    </div>
  )
}
