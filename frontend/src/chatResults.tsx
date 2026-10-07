import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import type { ChatProduct } from './api'

interface ChatResultsState {
  query: string | null
  products: ChatProduct[]
  show: (query: string, products: ChatProduct[]) => void
  clear: () => void
}

const ChatResultsContext = createContext<ChatResultsState | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState<string | null>(null)
  const [products, setProducts] = useState<ChatProduct[]>([])

  const value = useMemo<ChatResultsState>(
    () => ({
      query,
      products,
      show: (q, p) => {
        setQuery(q)
        setProducts(p)
      },
      clear: () => {
        setQuery(null)
        setProducts([])
      },
    }),
    [query, products],
  )

  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}

export function useChatResults() {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used within ChatResultsProvider')
  return ctx
}
