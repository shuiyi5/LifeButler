import type { FC } from 'react';
import { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useThemeStore } from '../stores/themeStore';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, Monitor } from 'lucide-react';

export const SettingsPage: FC = () => {
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useThemeStore();
  const navigate = useNavigate();

  const [nickname, setNickname] = useState(user?.nickname || '');
  const [city, setCity] = useState(localStorage.getItem('default_city') || '');
  const [apiKey, setApiKey] = useState('');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSave = () => {
    localStorage.setItem('default_city', city);
    if (apiKey) localStorage.setItem('qweather_key', apiKey);
  };

  const themes = [
    { value: 'light' as const, label: '浅色', icon: Sun },
    { value: 'dark' as const, label: '深色', icon: Moon },
    { value: 'auto' as const, label: '跟随系统', icon: Monitor },
  ];

  return (
    <div className="h-full overflow-y-auto p-6">
      <h1 className="text-h1 text-text-primary dark:text-text-primary-dark mb-6">设置</h1>

      <div className="space-y-4">
        <div className="card">
          <h2 className="text-h3 text-text-primary dark:text-text-primary-dark mb-4">个人信息</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-text-primary dark:text-text-primary-dark mb-2">昵称</label>
              <input value={nickname} onChange={(e) => setNickname(e.target.value)} className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm text-text-primary dark:text-text-primary-dark mb-2">邮箱</label>
              <input value={user?.email} disabled className="input-field w-full opacity-60" />
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-h3 text-text-primary dark:text-text-primary-dark mb-4">偏好设置</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-text-primary dark:text-text-primary-dark mb-2">默认城市</label>
              <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="北京" className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm text-text-primary dark:text-text-primary-dark mb-2">和风天气 API Key</label>
              <input value={apiKey} onChange={(e) => setApiKey(e.target.value)} type="password" placeholder="可选" className="input-field w-full" />
            </div>
          </div>
          <button onClick={handleSave} className="btn-primary mt-4">保存设置</button>
        </div>

        <div className="card">
          <h2 className="text-h3 text-text-primary dark:text-text-primary-dark mb-4">外观</h2>
          <div className="flex gap-3">
            {themes.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                onClick={() => setTheme(value)}
                className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-btn border-2 transition-all ${
                  theme === value
                    ? 'border-primary bg-primary-light dark:bg-primary/10'
                    : 'border-border dark:border-border-dark hover:border-primary/50'
                }`}
              >
                <Icon className={`w-6 h-6 ${theme === value ? 'text-primary' : 'text-text-secondary dark:text-text-secondary-dark'}`} />
                <span className={`text-sm ${theme === value ? 'text-primary font-medium' : 'text-text-secondary dark:text-text-secondary-dark'}`}>
                  {label}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-h3 text-text-primary dark:text-text-primary-dark mb-4">账户</h2>
          <button onClick={handleLogout} className="btn-danger">退出登录</button>
        </div>
      </div>
    </div>
  );
};
