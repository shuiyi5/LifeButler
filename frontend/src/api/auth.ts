import api from '../services/api';

export const authAPI = {
  login: async (email: string, password: string) => {
    const { data } = await api.post('/auth/login', { email, password });
    return data;
  },
  register: async (email: string, password: string) => {
    const { data } = await api.post('/auth/register', { email, password });
    return data;
  }
};
