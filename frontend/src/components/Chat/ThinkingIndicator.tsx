import type { FC } from 'react';

interface ThinkingIndicatorProps {
  stage?: 'thinking' | 'tool_calling' | 'generating';
  toolName?: string;
}

export const ThinkingIndicator: FC<ThinkingIndicatorProps> = ({ stage = 'thinking', toolName }) => {
  const labels: Record<string, string> = {
    thinking: '正在思考',
    tool_calling: toolName ? `正在调用 ${toolName}` : '正在调用工具',
    generating: '正在生成回复',
  };

  return (
    <div className="flex justify-start mb-3 animate-fade-in">
      <div className="bg-white dark:bg-surface-dark border border-gray-100 dark:border-border-dark rounded-2xl px-4 py-2.5 shadow-low">
        <div className="flex items-center gap-2.5">
          <div className="relative flex items-center justify-center w-5 h-5">
            <span className="absolute inset-0 rounded-full bg-primary/20 animate-pulse-soft" />
            <span className="relative w-2 h-2 bg-primary rounded-full" />
          </div>
          <span className="text-sm text-text-secondary dark:text-text-secondary-dark">
            {labels[stage] || '思考中'}
          </span>
          <div className="flex gap-0.5">
            <span className="w-1 h-1 bg-text-secondary/40 rounded-full animate-bounce-dot" style={{ animationDelay: '0s' }} />
            <span className="w-1 h-1 bg-text-secondary/40 rounded-full animate-bounce-dot" style={{ animationDelay: '0.2s' }} />
            <span className="w-1 h-1 bg-text-secondary/40 rounded-full animate-bounce-dot" style={{ animationDelay: '0.4s' }} />
          </div>
        </div>
      </div>
    </div>
  );
};
