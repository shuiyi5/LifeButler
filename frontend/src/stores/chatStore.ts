import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isStreaming?: boolean
}

interface ChatState {
  messages: Message[]
  isLoading: boolean
  addMessage: (message: Message) => void
  updateLastMessage: (content: string) => void
  setLoading: (loading: boolean) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,

  addMessage: (message: Message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  updateLastMessage: (content: string) =>
    set((state) => {
      const messages = [...state.messages]
      if (messages.length > 0) {
        messages[messages.length - 1] = {
          ...messages[messages.length - 1],
          content,
          isStreaming: false,
        }
      }
      return { messages }
    }),

  setLoading: (isLoading: boolean) => set({ isLoading }),

  clearMessages: () => set({ messages: [] }),
}))
