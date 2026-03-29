import { chatAPI } from './api'

export const chatService = {
  getHistory: (limit = 50) => chatAPI.getHistory(limit),

  connectWebSocket: (url: string, token: string) => {
    const ws = new WebSocket(url)
    ws.onopen = () => ws.send(JSON.stringify({ token }))
    return ws
  },
}
