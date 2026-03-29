import type { FC } from 'react';
import { DailyOverview } from '../components/Dashboard/DailyOverview';

export const HomePage: FC = () => {
  return (
    <div className="h-full overflow-y-auto p-6">
      <DailyOverview />
    </div>
  );
};
