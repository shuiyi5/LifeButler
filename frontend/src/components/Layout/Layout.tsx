import type { FC, ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { BottomNav } from './BottomNav';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-background dark:bg-background-dark">
      <Sidebar />
      <main className="flex-1 overflow-hidden pb-16 md:pb-0">
        {children}
      </main>
      <BottomNav />
    </div>
  );
};
