import type { FC } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, MessageCircle, LayoutDashboard, Settings, Calendar, CheckSquare, DollarSign, ShoppingCart, StickyNote, BookOpen, Apple } from 'lucide-react';

export const Sidebar: FC = () => {
  const location = useLocation();

  const mainNav = [
    { path: '/', icon: Home, label: '首页' },
    { path: '/chat', icon: MessageCircle, label: '对话' },
    { path: '/dashboard', icon: LayoutDashboard, label: '面板' }
  ];

  const toolsNav = [
    { path: '/calendar', icon: Calendar, label: '日程' },
    { path: '/todos', icon: CheckSquare, label: '待办' },
    { path: '/finance', icon: DollarSign, label: '记账' },
    { path: '/shopping', icon: ShoppingCart, label: '购物清单' },
    { path: '/notes', icon: StickyNote, label: '笔记' },
    { path: '/reading', icon: BookOpen, label: '读书' },
    { path: '/health', icon: Apple, label: '饮食健康' },
  ];

  return (
    <aside className="hidden md:flex flex-col w-64 bg-surface dark:bg-surface-dark border-r border-border dark:border-border-dark h-screen">
      <div className="p-6 border-b border-border dark:border-border-dark">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-2xl">
            🏠
          </div>
          <span className="text-xl font-semibold text-text-primary dark:text-text-primary-dark">LifeButler</span>
        </div>
      </div>
      <nav className="flex-1 p-4 overflow-y-auto">
        <div className="mb-6">
          {mainNav.map(({ path, icon: Icon, label }) => {
            const isActive = location.pathname === path;
            return (
              <Link key={path} to={path} className={`sidebar-item ${isActive ? 'sidebar-item-active' : ''}`}>
                <Icon size={20} />
                <span>{label}</span>
              </Link>
            );
          })}
        </div>
        <div className="mb-2">
          <p className="text-xs text-text-secondary dark:text-text-secondary-dark px-4 mb-2">功能</p>
          {toolsNav.map(({ path, icon: Icon, label }) => {
            const isActive = location.pathname === path;
            return (
              <Link key={path} to={path} className={`sidebar-item ${isActive ? 'sidebar-item-active' : ''}`}>
                <Icon size={20} />
                <span>{label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
      <div className="p-4 border-t border-border dark:border-border-dark">
        <Link to="/settings" className="sidebar-item">
          <Settings size={20} />
          <span>设置</span>
        </Link>
      </div>
    </aside>
  );
};
