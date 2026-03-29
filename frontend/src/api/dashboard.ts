import api from '../services/api';

export const dashboardAPI = {
  getOverview: async () => {
    const { data } = await api.get('/dashboard/overview');
    return data;
  }
};
