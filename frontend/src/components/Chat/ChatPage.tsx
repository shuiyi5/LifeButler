import type { FC } from 'react';
import { useState, useEffect, useRef } from 'react';
import { ChatBubble } from './ChatBubble';
import { ChatInput } from './ChatInput';
import { ThinkingIndicator } from './ThinkingIndicator';
import { useAuthStore } from '../../stores/authStore';
import { chatAPI } from '../../services/api';

interface ToolStep {
  name: string;
  input?: any;
  result?: string;
  status: 'running' | 'done' | 'error';
}

interface Message {
  role: 'user' | 'assistant' | 'tool_group';
  content: string;
  timestamp: string;
  toolSteps?: ToolStep[];
  isStreaming?: boolean;
  suggestions?: string[];
}

export const ChatPage: FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [thinkingStage, setThinkingStage] = useState<'thinking' | 'tool_calling' | 'generating' | null>(null);
  const [currentToolName, setCurrentToolName] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentToolGroupRef = useRef<ToolStep[]>([]);
  const { token } = useAuthStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, thinkingStage]);

  // 加载历史记录
  useEffect(() => {
    if (!token) return;
    chatAPI.getHistory(50).then((res) => {
      const history = res.data.messages || [];
      if (history.length > 0) {
        setMessages(history.map((msg: { role: string; content: string }) => ({
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: '',
        })));
      }
      setHistoryLoaded(true);
    }).catch(() => {
      setHistoryLoaded(true);
    });
  }, [token]);

  // WebSocket连接（历史加载完后再连）
  useEffect(() => {
    if (!token || !historyLoaded) return;

    const ws = new WebSocket(`ws://localhost:8000/api/chat/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      ws.send(JSON.stringify({ token }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'thinking') {
        setThinkingStage('thinking');
      } else if (data.type === 'tool_call') {
        setThinkingStage('tool_calling');
        setCurrentToolName(data.tool);
        currentToolGroupRef.current.push({
          name: data.tool,
          input: data.input,
          status: 'running',
        });
      } else if (data.type === 'tool_result') {
        const idx = currentToolGroupRef.current.findIndex(
          s => s.name === data.tool && s.status === 'running'
        );
        if (idx !== -1) {
          currentToolGroupRef.current[idx].result = data.result;
          currentToolGroupRef.current[idx].status = 'done';
        }
      } else if (data.type === 'chunk') {
        setThinkingStage(null);
        if (currentToolGroupRef.current.length > 0) {
          setMessages((prev) => {
            const hasToolGroup = prev[prev.length - 1]?.role === 'tool_group';
            if (!hasToolGroup) {
              return [...prev, {
                role: 'tool_group' as const,
                content: '',
                toolSteps: [...currentToolGroupRef.current],
                timestamp: new Date().toLocaleTimeString(),
              }];
            }
            return prev;
          });
          currentToolGroupRef.current = [];
        }
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === 'assistant' && last.isStreaming) {
            return [...prev.slice(0, -1), { ...last, content: last.content + data.content }];
          }
          return [...prev, {
            role: 'assistant',
            content: data.content,
            timestamp: new Date().toLocaleTimeString(),
            isStreaming: true,
          }];
        });
      } else if (data.type === 'done') {
        setThinkingStage(null);
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.isStreaming) {
            const suggestions = parseSuggestions(last.content);
            return [...prev.slice(0, -1), { ...last, isStreaming: false, suggestions }];
          }
          return prev;
        });
      }
    };

    ws.onclose = () => setIsConnected(false);

    return () => ws.close();
  }, [token, historyLoaded]);

  /** 从回复中提取建议（末尾的列表项或问号结尾的短句） */
  const parseSuggestions = (content: string): string[] | undefined => {
    const suggestions: string[] = [];
    const lines = content.split('\n').map(l => l.trim()).filter(Boolean);
    // 倒序扫描最后几行，寻找列表项
    for (let i = lines.length - 1; i >= Math.max(0, lines.length - 6); i--) {
      const m = lines[i].match(/^(?:[•\-\*✅🔹▸]|\d+[.)、])\s*(.+)$/);
      if (m) suggestions.unshift(m[1].replace(/\*+/g, '').trim());
    }
    if (suggestions.length > 0) return suggestions.slice(0, 3);
    // 也寻找问号结尾的句子作为建议
    const lastLine = lines[lines.length - 1] || '';
    if (lastLine.includes('？') || lastLine.includes('?')) return undefined;
    return undefined;
  };

  const handleSend = (content: string, image?: File) => {
    if (!wsRef.current || !isConnected) return;
    let displayContent = content;
    if (image) {
      displayContent = content ? `${content}\n[图片: ${image.name}]` : `[图片: ${image.name}]`;
    }
    const userMsg: Message = {
      role: 'user',
      content: displayContent,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    wsRef.current.send(JSON.stringify({ message: content, image: image?.name }));
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && !thinkingStage && (
          <div className="flex flex-col items-center justify-center h-full text-text-secondary dark:text-text-secondary-dark">
            <p className="text-lg mb-2">👋 你好，我是 LifeButler</p>
            <p className="text-sm mb-6">你的 AI 生活管家，试试下面的操作：</p>
            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              {['记一笔50元午餐', '创建一个运动习惯', '明天下午3点开会', '查看本月支出'].map((s) => (
                <button
                  key={s}
                  onClick={() => handleSend(s)}
                  disabled={!isConnected}
                  className="px-3 py-1.5 text-sm bg-white dark:bg-surface-dark border border-border dark:border-border-dark rounded-full hover:border-primary hover:text-primary transition-colors disabled:opacity-50"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <ChatBubble key={idx} {...msg} onSuggestionClick={handleSend} />
        ))}
        {thinkingStage && <ThinkingIndicator stage={thinkingStage} toolName={currentToolName} />}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSend={handleSend} disabled={!isConnected} />
    </div>
  );
};
