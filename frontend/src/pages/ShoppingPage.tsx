import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { ShoppingCart, Plus, Trash2, X, Check, CheckCircle2, Circle } from 'lucide-react'
import { shoppingAPI } from '../services/api'

interface Item { id: number; name: string; category: string; quantity: number; unit: string; is_purchased: boolean }

const CATS = ['蔬菜','水果','肉类','饮品','日用','其他']

export const ShoppingPage: FC = () => {
  const [items, setItems] = useState<Item[]>([])
  const [loading, setLoading] = useState(true)
  const [showPurchased, setShowPurchased] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', category: '其他', quantity: 1, unit: '个' })

  const fetch = useCallback(async () => {
    setLoading(true)
    try { const r = await shoppingAPI.list(showPurchased); setItems(r.data) } catch { setItems([]) }
    finally { setLoading(false) }
  }, [showPurchased])
  useEffect(() => { fetch() }, [fetch])

  const handleAdd = async () => {
    if (!form.name) return
    await shoppingAPI.create(form)
    setForm({ name: '', category: '其他', quantity: 1, unit: '个' }); setShowForm(false); fetch()
  }
  const handleToggle = async (item: Item) => {
    await shoppingAPI.update(item.id, { is_purchased: !item.is_purchased }); fetch()
  }
  const handleDelete = async (id: number) => { await shoppingAPI.delete(id); fetch() }
  const handleClear = async () => { await shoppingAPI.clearPurchased(); fetch() }

  const grouped = items.reduce<Record<string, Item[]>>((acc, i) => { (acc[i.category] = acc[i.category] || []).push(i); return acc }, {})
  const purchasedCount = items.filter(i => i.is_purchased).length

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 text-text-primary dark:text-text-primary-dark flex items-center gap-2"><ShoppingCart size={28} className="text-primary" />购物清单</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-1.5 text-sm"><Plus size={16} />添加</button>
      </div>
      <div className="flex gap-2 mb-4">
        <button onClick={() => setShowPurchased(false)} className={`px-3 py-1 text-xs rounded-full ${!showPurchased ? 'bg-primary text-white' : 'bg-soft text-text-secondary'}`}>待购</button>
        <button onClick={() => setShowPurchased(true)} className={`px-3 py-1 text-xs rounded-full ${showPurchased ? 'bg-primary text-white' : 'bg-soft text-text-secondary'}`}>全部</button>
        {purchasedCount > 0 && <button onClick={handleClear} className="ml-auto px-3 py-1 text-xs rounded-full text-error bg-error/10">清空已购</button>}
      </div>
      {loading ? <div className="text-center py-20 text-text-secondary">加载中...</div> : items.length === 0 ? (
        <div className="text-center py-20 text-text-secondary"><ShoppingCart size={48} className="mx-auto mb-3 opacity-30" /><p>购物清单为空</p><p className="text-xs mt-1">点击「添加」或聊天中说「购物清单加上牛奶」</p></div>
      ) : (
        <div className="space-y-4">
          {Object.entries(grouped).map(([cat, catItems]) => (
            <div key={cat}>
              <p className="text-xs font-medium text-text-secondary mb-2">{cat}</p>
              <div className="space-y-1">
                {catItems.map(item => (
                  <div key={item.id} className={`flex items-center gap-3 bg-surface dark:bg-surface-dark rounded-xl px-4 py-2.5 border border-border dark:border-border-dark group ${item.is_purchased ? 'opacity-50' : ''}`}>
                    <button onClick={() => handleToggle(item)}>{item.is_purchased ? <CheckCircle2 size={20} className="text-secondary" /> : <Circle size={20} className="text-text-secondary/40" />}</button>
                    <span className={`flex-1 text-sm ${item.is_purchased ? 'line-through text-text-secondary' : 'text-text-primary dark:text-text-primary-dark'}`}>{item.name}</span>
                    <span className="text-xs text-text-secondary">{item.quantity}{item.unit}</span>
                    <button onClick={() => handleDelete(item.id)} className="opacity-0 group-hover:opacity-100 text-text-secondary hover:text-error"><Trash2 size={14} /></button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
      {showForm && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={() => setShowForm(false)}>
          <div className="bg-surface dark:bg-surface-dark rounded-2xl p-6 w-full max-w-sm shadow-high animate-scale-in" onClick={e => e.stopPropagation()}>
            <h3 className="text-h3 text-text-primary dark:text-text-primary-dark mb-4">添加商品</h3>
            <div className="space-y-3">
              <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="商品名称" className="input-field w-full" />
              <div className="flex flex-wrap gap-1">{CATS.map(c => <button key={c} onClick={() => setForm({...form, category: c})} className={`px-3 py-1 text-xs rounded-full ${form.category === c ? 'bg-primary text-white' : 'bg-soft text-text-secondary'}`}>{c}</button>)}</div>
              <div className="flex gap-2">
                <input type="number" value={form.quantity} onChange={e => setForm({...form, quantity: Number(e.target.value)})} className="input-field w-20" min={1} />
                <input value={form.unit} onChange={e => setForm({...form, unit: e.target.value})} className="input-field w-20" placeholder="单位" />
              </div>
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
