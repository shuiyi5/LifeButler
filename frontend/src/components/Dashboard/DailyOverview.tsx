import type { FC } from 'react';
import { useState, useEffect } from 'react';
import { dashboardAPI } from '../../api/dashboard';
import { Calendar, CheckSquare, DollarSign } from 'lucide-react';

interface OverviewData {
  greeting: string;
  events: Array<{ title: string; start_time: string }>;
  todos: Array<{ title: string; priority: string }>;
  expenses: { total: number; count: number };
}

export const DailyOverview: FC = () => {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.getOverview()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-gray-500">加载中...</div>;
  if (!data) return null;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">{data.greeting}</h2>
      
      <div className="space-y-4">
        {data.events.length > 0 && (
          <div className="flex gap-3">
            <Calendar className="text-primary flex-shrink-0" size={20} />
            <div>
              <h3 className="font-medium text-gray-700 mb-2">今日日程</h3>
              {data.events.map((e, i) => (
                <p key={i} className="text-sm text-gray-600">{e.start_time} - {e.title}</p>
              ))}
            </div>
          </div>
        )}

        {data.todos.length > 0 && (
          <div className="flex gap-3">
            <CheckSquare className="text-primary flex-shrink-0" size={20} />
            <div>
              <h3 className="font-medium text-gray-700 mb-2">待办事项</h3>
              {data.todos.map((t, i) => (
                <p key={i} className="text-sm text-gray-600">{t.title}</p>
              ))}
            </div>
          </div>
        )}

        {data.expenses.count > 0 && (
          <div className="flex gap-3">
            <DollarSign className="text-primary flex-shrink-0" size={20} />
            <div>
              <h3 className="font-medium text-gray-700 mb-2">今日消费</h3>
              <p className="text-sm text-gray-600">¥{data.expenses.total.toFixed(2)}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
