import type { FC } from 'react';
import { useState } from 'react';
import { ChevronDown, ChevronRight, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';

interface ToolStep {
  name: string;
  input?: any;
  result?: string;
  status: 'running' | 'done' | 'error';
}

interface ChatBubbleProps {
  role: 'user' | 'assistant' | 'tool_group';
  content: string;
  timestamp?: string;
  toolSteps?: ToolStep[];
  isStreaming?: boolean;
  suggestions?: string[];
  onSuggestionClick?: (text: string) => void;
}

const TOOL_LABELS: Record<string, string> = {
  calendar_create: '创建日程',
  calendar_query: '查询日程',
  calendar_update: '修改日程',
  calendar_delete: '删除日程',
  todo_create: '创建待办',
  todo_query: '查询待办',
  todo_update: '更新待办',
  todo_delete: '删除待办',
  weather_query: '查询天气',
  news_summary: '获取新闻',
  finance_record: '记账',
  finance_query: '查询账单',
  meal_record: '记录饮食',
  meal_query: '查询饮食',
  habit_create: '创建习惯',
  habit_checkin: '习惯打卡',
  habit_query: '查询习惯',
  shopping_add: '添加购物项',
  shopping_query: '查询购物清单',
  reading_create: '创建读书计划',
  reading_query: '查询读书进度',
  note_create: '创建笔记',
  note_query: '查询笔记',
};

const getToolLabel = (name: string) => TOOL_LABELS[name] || name;

const ToolStepItem: FC<{ step: ToolStep; isLast: boolean }> = ({ step, isLast }) => {
  const [showDetail, setShowDetail] = useState(false);
  const hasDetail = step.input || step.result;

  let parsedResult: any = null;
  if (step.result) {
    try { parsedResult = JSON.parse(step.result); } catch { parsedResult = step.result; }
  }

  return (
    <div className="relative">
      {/* Timeline connector */}
      {!isLast && (
        <div className="absolute left-[9px] top-[22px] w-[2px] h-[calc(100%-6px)] bg-gray-200 dark:bg-border-dark" />
      )}
      <div className="flex items-start gap-2.5">
        {/* Status icon */}
        <div className="flex-shrink-0 mt-0.5">
          {step.status === 'running' ? (
            <Loader2 size={18} className="text-primary animate-spin" />
          ) : step.status === 'error' ? (
            <AlertCircle size={18} className="text-error" />
          ) : (
            <CheckCircle2 size={18} className="text-secondary" />
          )}
        </div>
        {/* Content */}
        <div className="flex-1 min-w-0 pb-3">
          <button
            type="button"
            onClick={() => hasDetail && setShowDetail(!showDetail)}
            className={`flex items-center gap-1 text-sm font-medium ${
              step.status === 'running' ? 'text-primary' : 'text-text-primary dark:text-text-primary-dark'
            } ${hasDetail ? 'cursor-pointer hover:text-primary transition-colors' : 'cursor-default'}`}
          >
            <span>{getToolLabel(step.name)}</span>
            {hasDetail && (
              showDetail
                ? <ChevronDown size={14} className="text-text-secondary" />
                : <ChevronRight size={14} className="text-text-secondary" />
            )}
          </button>
          {/* Collapsed result hint */}
          {step.status === 'done' && !showDetail && parsedResult && (
            <p className="text-xs text-text-secondary dark:text-text-secondary-dark mt-0.5 truncate max-w-[200px]">
              {parsedResult?.error ? `错误: ${parsedResult.error}` : '执行成功'}
            </p>
          )}
          {/* Expanded detail */}
          {showDetail && (
            <div className="mt-1.5 space-y-1.5 animate-scale-in">
              {step.input && (
                <div className="rounded-lg bg-black/[0.03] dark:bg-white/[0.04] px-2.5 py-1.5">
                  <p className="text-[10px] font-medium text-text-secondary uppercase tracking-wider mb-0.5">参数</p>
                  <pre className="text-xs font-mono text-text-primary dark:text-text-primary-dark whitespace-pre-wrap break-all leading-relaxed">
                    {JSON.stringify(step.input, null, 2)}
                  </pre>
                </div>
              )}
              {step.result && (
                <div className="rounded-lg bg-black/[0.03] dark:bg-white/[0.04] px-2.5 py-1.5">
                  <p className="text-[10px] font-medium text-text-secondary uppercase tracking-wider mb-0.5">结果</p>
                  <pre className="text-xs font-mono text-text-primary dark:text-text-primary-dark whitespace-pre-wrap break-all leading-relaxed max-h-32 overflow-y-auto">
                    {typeof parsedResult === 'object' ? JSON.stringify(parsedResult, null, 2) : String(parsedResult)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ToolGroup: FC<{ steps: ToolStep[] }> = ({ steps }) => {
  const [collapsed, setCollapsed] = useState(false);
  const allDone = steps.every(s => s.status === 'done');
  const anyRunning = steps.some(s => s.status === 'running');

  return (
    <div className="flex justify-start mb-3 animate-slide-up">
      <div className={`border rounded-2xl px-3.5 py-2.5 max-w-[85%] transition-all duration-300 ${
        anyRunning
          ? 'bg-primary-light/50 dark:bg-primary/5 border-primary/20'
          : allDone
            ? 'bg-white dark:bg-surface-dark border-gray-100 dark:border-border-dark'
            : 'bg-error/5 border-error/20'
      }`}>
        {/* Header */}
        <button
          type="button"
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-2 w-full text-left"
        >
          {anyRunning ? (
            <Loader2 size={14} className="text-primary animate-spin flex-shrink-0" />
          ) : (
            <CheckCircle2 size={14} className="text-secondary flex-shrink-0" />
          )}
          <span className="text-xs font-medium text-text-secondary dark:text-text-secondary-dark">
            {anyRunning ? `执行中 (${steps.filter(s => s.status === 'done').length}/${steps.length})` : `已完成 ${steps.length} 个操作`}
          </span>
          {collapsed ? <ChevronRight size={12} className="ml-auto text-text-secondary/50" /> : <ChevronDown size={12} className="ml-auto text-text-secondary/50" />}
        </button>
        {/* Steps */}
        {!collapsed && (
          <div className="mt-2.5 ml-0.5">
            {steps.map((step, i) => (
              <ToolStepItem key={`${step.name}-${i}`} step={step} isLast={i === steps.length - 1} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export const ChatBubble: FC<ChatBubbleProps> = ({ role, content, timestamp, toolSteps, isStreaming, suggestions, onSuggestionClick }) => {
  const isUser = role === 'user';

  if (role === 'tool_group' && toolSteps) {
    return <ToolGroup steps={toolSteps} />;
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 animate-slide-up`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div className={isUser ? 'bubble-user' : 'bubble-assistant'}>
          <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">
            {content}
            {isStreaming && (
              <span className="inline-block w-0.5 h-4 bg-primary ml-0.5 align-text-bottom animate-cursor-blink" />
            )}
          </p>
        </div>
        {suggestions && suggestions.length > 0 && !isUser && (
          <div className="flex flex-wrap gap-2 mt-2">
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => onSuggestionClick?.(s)}
                className="px-3 py-1 text-xs bg-primary-light dark:bg-primary/10 text-primary dark:text-primary-dark rounded-full hover:bg-primary hover:text-white transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}
        {timestamp && (
          <p className={`text-[11px] text-text-secondary dark:text-text-secondary-dark mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );
};
