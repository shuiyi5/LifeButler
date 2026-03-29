import type { FC } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, MessageCircle, LayoutDashboard, Settings } from 'lucide-react';

export const BottomNav: FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: '首页' },
    { path: '/chat', icon: MessageCircle, label: '对话' },
    { path: '/dashboard', icon: LayoutDashboard, label: '面板' },
    { path: '/settings', icon: Settings, label: '设置' }
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-surface dark:bg-surface-dark border-t border-border dark:border-border-dark px-2 py-2 safe-area-bottom">
      <div className="flex justify-around">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <Link key={path} to={path} className={`nav-item ${isActive ? 'nav-item-active' : ''}`}>
              <Icon size={22} />
              <span className="text-xs">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};
