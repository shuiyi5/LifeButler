import type { FC } from 'react'
import { useState, useEffect, useCallback } from 'react'
import { DollarSign, TrendingUp, TrendingDown, Inbox } from 'lucide-react'
import { dashboardAPI } from '../../services/api'

interface FinanceData {
  income: number
  expense: number
  categories: { name: string; amount: number }[]
}

const CATEGORY_COLORS: Record<string, string> = {
  '餐饮': '#E8835A', '交通': '#7BB6A4', '购物': '#F2B84B',
  '住房': '#9B8E82', '娱乐': '#E06B5E', '医疗': '#8DC7B5',
  '教育': '#D6744D', '其他': '#C4653F',
}

export const FinanceChart: FC<{ refreshKey?: number }> = ({ refreshKey }) => {
  const [data, setData] = useState<FinanceData | null>(null)
  const [period, setPeriod] = useState<'week' | 'month'>('month')
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const res = await dashboardAPI.getFinance(period)
      setData(res.data)
    } catch {
      setData({ income: 0, expense: 0, categories: [] })
    } finally {
      setLoading(false)
    }
  }, [period])

  useEffect(() => { fetchData() }, [fetchData, refreshKey])

  const maxAmount = data?.categories?.length ? Math.max(...data.categories.map((c) => c.amount)) : 0

  return (
    <div className="bg-surface dark:bg-surface-dark rounded-card shadow-low p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-h3 text-text-primary dark:text-text-primary-dark flex items-center gap-2">
          <DollarSign size={20} className="text-primary" />
          财务统计
        </h2>
        <div className="flex gap-1 bg-soft dark:bg-background-dark rounded-lg p-1">
          <button
            onClick={() => setPeriod('week')}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              period === 'week' ? 'bg-primary text-white' : 'text-text-secondary dark:text-text-secondary-dark'
            }`}
          >
            本周
          </button>
          <button
            onClick={() => setPeriod('month')}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              period === 'month' ? 'bg-primary text-white' : 'text-text-secondary dark:text-text-secondary-dark'
            }`}
          >
            本月
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32 text-text-secondary">加载中...</div>
      ) : (
        <>
          <div className="flex gap-4 mb-6">
            <div className="flex-1 bg-green-50 dark:bg-green-900/20 rounded-xl p-3">
              <div className="flex items-center gap-1 text-green-600 dark:text-green-400 text-xs mb-1">
                <TrendingUp size={14} /> 收入
              </div>
              <p className="text-lg font-semibold text-green-700 dark:text-green-300">¥{(data?.income ?? 0).toLocaleString()}</p>
            </div>
            <div className="flex-1 bg-red-50 dark:bg-red-900/20 rounded-xl p-3">
              <div className="flex items-center gap-1 text-red-500 dark:text-red-400 text-xs mb-1">
                <TrendingDown size={14} /> 支出
              </div>
              <p className="text-lg font-semibold text-red-600 dark:text-red-300">¥{(data?.expense ?? 0).toLocaleString()}</p>
            </div>
          </div>

          {data?.categories?.length ? (
            <div className="space-y-3">
              <p className="text-caption text-text-secondary dark:text-text-secondary-dark">支出分类</p>
              {data.categories.map((cat) => (
                <div key={cat.name} className="flex items-center gap-3">
                  <span className="text-sm text-text-primary dark:text-text-primary-dark w-12">{cat.name}</span>
                  <div className="flex-1 bg-soft dark:bg-background-dark rounded-full h-4 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${maxAmount > 0 ? (cat.amount / maxAmount) * 100 : 0}%`, backgroundColor: CATEGORY_COLORS[cat.name] || '#9B8E82' }}
                    />
                  </div>
                  <span className="text-sm text-text-secondary dark:text-text-secondary-dark w-16 text-right">¥{cat.amount}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-6 text-text-secondary dark:text-text-secondary-dark">
              <Inbox size={32} className="mb-2 opacity-40" />
              <p className="text-sm">暂无记账数据</p>
              <p className="text-xs mt-1">在聊天中说「记一笔50元午餐」即可开始记账</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
