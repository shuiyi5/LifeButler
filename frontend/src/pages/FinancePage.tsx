import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { DollarSign, Plus, Trash2, X, Check, TrendingUp, TrendingDown, ArrowUpDown } from 'lucide-react'
import { financeAPI } from '../services/api'

interface Txn {
  id: number; type: string; amount: number
  category: string; description: string; date: string
}

const EXPENSE_CATS = ['餐饮','交通','购物','住房','娱乐','医疗','教育','其他']
const INCOME_CATS = ['工资','奖金','投资','兼职','其他']
const CAT_COLORS: Record<string, string> = {
  '餐饮':'#E8835A','交通':'#7BB6A4','购物':'#F2B84B','住房':'#9B8E82',
  '娱乐':'#E06B5E','医疗':'#8DC7B5','教育':'#D6744D','其他':'#C4653F',
  '工资':'#7BB6A4','奖金':'#F2B84B','投资':'#E8835A','兼职':'#9B8E82',
}

export const FinancePage: FC = () => {
  const [txns, setTxns] = useState<Txn[]>([])
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState<'week' | 'month'>('month')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [form, setForm] = useState({ type: 'expense', amount: '', category: '餐饮', description: '', date: new Date().toISOString().split('T')[0] })

  const fetchTxns = useCallback(async () => {
    setLoading(true)
    try {
      const res = await financeAPI.list(period, typeFilter || undefined)
      setTxns(res.data)
    } catch { setTxns([]) }
    finally { setLoading(false) }
  }, [period, typeFilter])

  useEffect(() => { fetchTxns() }, [fetchTxns])

  const income = txns.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0)
  const expense = txns.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0)

  const resetForm = () => { setForm({ type: 'expense', amount: '', category: '餐饮', description: '', date: new Date().toISOString().split('T')[0] }); setEditId(null); setShowForm(false) }

  const handleSave = async () => {
    const amt = parseFloat(form.amount)
    if (!amt || amt <= 0) return
    const payload = { ...form, amount: amt }
    if (editId) { await financeAPI.update(editId, payload) }
    else { await financeAPI.create(payload) }
    resetForm(); fetchTxns()
  }

  const handleEdit = (t: Txn) => {
    setForm({ type: t.type, amount: String(t.amount), category: t.category, description: t.description, date: t.date })
    setEditId(t.id); setShowForm(true)
  }

  const handleDelete = async (id: number) => { await financeAPI.delete(id); fetchTxns() }

  const cats = form.type === 'income' ? INCOME_CATS : EXPENSE_CATS

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-h1 text-text-primary dark:text-text-primary-dark flex items-center gap-2"><DollarSign size={28} className="text-primary" />记账管理</h1>
        <button onClick={() => { resetForm(); setShowForm(true) }} className="btn-primary flex items-center gap-1.5 text-sm"><Plus size={16} />记一笔</button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4">
          <div className="flex items-center gap-1 text-green-600 dark:text-green-400 text-xs mb-1"><TrendingUp size={14} />收入</div>
          <p className="text-xl font-semibold text-green-700 dark:text-green-300">¥{income.toLocaleString()}</p>
        </div>
        <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-4">
          <div className="flex items-center gap-1 text-red-500 dark:text-red-400 text-xs mb-1"><TrendingDown size={14} />支出</div>
          <p className="text-xl font-semibold text-red-600 dark:text-red-300">¥{expense.toLocaleString()}</p>
        </div>
        <div className="bg-primary-light/50 dark:bg-primary/10 rounded-xl p-4">
          <div className="flex items-center gap-1 text-primary text-xs mb-1"><ArrowUpDown size={14} />结余</div>
          <p className={`text-xl font-semibold ${income - expense >= 0 ? 'text-green-700 dark:text-green-300' : 'text-red-600 dark:text-red-300'}`}>¥{(income - expense).toLocaleString()}</p>
        </div>
      </div>

      {/* 筛选 */}
      <div className="flex gap-2 mb-4">
        <div className="flex gap-1 bg-soft dark:bg-surface-dark rounded-lg p-1">
          {(['week','month'] as const).map(p => (
            <button key={p} onClick={() => setPeriod(p)} className={`px-3 py-1 text-xs rounded-md transition-colors ${period === p ? 'bg-primary text-white' : 'text-text-secondary'}`}>
              {p === 'week' ? '本周' : '本月'}
            </button>
          ))}
        </div>
        <div className="flex gap-1 bg-soft dark:bg-surface-dark rounded-lg p-1">
          {[{v:'',l:'全部'},{v:'expense',l:'支出'},{v:'income',l:'收入'}].map(f => (
            <button key={f.v} onClick={() => setTypeFilter(f.v)} className={`px-3 py-1 text-xs rounded-md transition-colors ${typeFilter === f.v ? 'bg-primary text-white' : 'text-text-secondary'}`}>
              {f.l}
            </button>
          ))}
        </div>
      </div>

      {/* 列表 */}
      {loading ? <div className="text-center py-20 text-text-secondary">加载中...</div> : txns.length === 0 ? (
        <div className="text-center py-20 text-text-secondary dark:text-text-secondary-dark">
          <DollarSign size={48} className="mx-auto mb-3 opacity-30" />
          <p>暂无记账数据</p>
          <p className="text-xs mt-1">点击「记一笔」或在聊天中说「午饭花了35块」</p>
        </div>
      ) : (
        <div className="space-y-2">
          {txns.map(t => (
            <div key={t.id} className="flex items-center gap-3 bg-surface dark:bg-surface-dark rounded-xl px-4 py-3 border border-border dark:border-border-dark hover:shadow-low transition-all group cursor-pointer" onClick={() => handleEdit(t)}>
              <div className="w-9 h-9 rounded-full flex items-center justify-center text-white text-sm flex-shrink-0" style={{ backgroundColor: CAT_COLORS[t.category] || '#9B8E82' }}>
                {t.type === 'income' ? '+' : '-'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary dark:text-text-primary-dark">{t.description || t.category}</p>
                <p className="text-xs text-text-secondary dark:text-text-secondary-dark">{t.category} · {t.date}</p>
              </div>
              <span className={`text-sm font-semibold ${t.type === 'income' ? 'text-green-600' : 'text-red-500'}`}>
                {t.type === 'income' ? '+' : '-'}¥{t.amount.toFixed(2)}
              </span>
              <button onClick={(e) => { e.stopPropagation(); handleDelete(t.id) }} className="opacity-0 group-hover:opacity-100 transition-opacity text-text-secondary hover:text-error"><Trash2 size={16} /></button>
            </div>
          ))}
        </div>
      )}

      {/* 弹窗表单 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={resetForm}>
          <div className="bg-surface dark:bg-surface-dark rounded-2xl p-6 w-full max-w-md shadow-high animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-h3 text-text-primary dark:text-text-primary-dark">{editId ? '编辑记录' : '记一笔'}</h3>
              <button onClick={resetForm}><X size={20} className="text-text-secondary" /></button>
            </div>
            <div className="space-y-3">
              {/* 收支切换 */}
              <div className="flex gap-2">
                <button onClick={() => setForm({...form, type: 'expense', category: '餐饮'})} className={`flex-1 py-2 text-sm rounded-lg border transition-colors ${form.type === 'expense' ? 'border-red-400 bg-red-50 dark:bg-red-900/20 text-red-500' : 'border-border dark:border-border-dark text-text-secondary'}`}>支出</button>
                <button onClick={() => setForm({...form, type: 'income', category: '工资'})} className={`flex-1 py-2 text-sm rounded-lg border transition-colors ${form.type === 'income' ? 'border-green-400 bg-green-50 dark:bg-green-900/20 text-green-600' : 'border-border dark:border-border-dark text-text-secondary'}`}>收入</button>
              </div>
              <input type="number" value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="金额" className="input-field w-full text-xl font-semibold" step="0.01" />
              {/* 分类选择 */}
              <div className="flex flex-wrap gap-2">
                {cats.map(c => (
                  <button key={c} onClick={() => setForm({...form, category: c})} className={`px-3 py-1 text-xs rounded-full transition-colors ${form.category === c ? 'bg-primary text-white' : 'bg-soft dark:bg-background-dark text-text-secondary'}`}>{c}</button>
                ))}
              </div>
              <input value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="备注（可选）" className="input-field w-full" />
              <input type="date" value={form.date} onChange={e => setForm({...form, date: e.target.value})} className="input-field w-full" />
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
