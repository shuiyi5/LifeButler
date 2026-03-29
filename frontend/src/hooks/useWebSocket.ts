import { useEffect, useRef, useState } from 'react'

export const useWebSocket = (url: string, token: string | null) => {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!token) return
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
      ws.send(JSON.stringify({ token }))
    }
    ws.onclose = () => setIsConnected(false)

    return () => ws.close()
  }, [url, token])

  return { ws: wsRef.current, isConnected }
}
