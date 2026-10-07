import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useMatch } from 'react-router-dom'
import { formatPrice, getChatHistory, imageUrl, sendChat, type ChatProduct } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'

interface Message {
  role: 'user' | 'assistant'
  content: string
  products?: ChatProduct[]
}

const GREETING: Message = {
  role: 'assistant',
  content: 'Hi, I’m the Campus Customs assistant! Ask me about our Yale gear, sizes, or stock.',
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)
  const { show } = useChatResults()
  const { user, token } = useAuth()

  // The product the shopper is currently viewing, if on a product page.
  const productMatch = useMatch('/products/:productId')
  const currentProductId = productMatch?.params.productId ?? null

  // Load (or clear) saved history whenever the signed-in user changes.
  useEffect(() => {
    if (!token) {
      setMessages([GREETING])
      return
    }
    let cancelled = false
    getChatHistory(token)
      .then((res) => {
        if (cancelled) return
        if (res.messages.length === 0) {
          setMessages([GREETING])
          return
        }
        setMessages(
          res.messages.map((m) => ({
            role: m.role,
            content: m.content,
            products: m.products,
          })),
        )
      })
      .catch(() => {
        if (!cancelled) setMessages([GREETING])
      })
    return () => {
      cancelled = true
    }
  }, [token, user?.id])

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight })
  }, [messages, open])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    setMessages((m) => [...m, { role: 'user', content: text }])
    setInput('')
    setSending(true)
    try {
      const res = await sendChat(text, { token, currentProductId })
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: res.reply, products: res.products },
      ])
      // Also surface the matches on the page itself, not just in the chat bubble.
      if (res.products.length > 0) {
        show(text, res.products)
      }
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: 'Sorry, I couldn’t reach the server. Please try again.' },
      ])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" aria-label="Chat with Campus Customs">
          <header className="chat-header">
            <span>Campus Customs Chat</span>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </header>
          <div className="chat-messages" ref={listRef}>
            {messages.map((m, i) => (
              <div key={i} className="chat-turn">
                <div className={`chat-bubble ${m.role}`}>{m.content}</div>
                {m.products && m.products.length > 0 && (
                  <div className="chat-products">
                    {m.products.map((p) => (
                      <Link
                        key={p.product_id}
                        to={`/products/${p.product_id}`}
                        className="chat-product"
                        onClick={() => setOpen(false)}
                      >
                        <img src={imageUrl(p.image_url)} alt={p.name} loading="lazy" />
                        <div className="chat-product-info">
                          <span className="chat-product-name">{p.name}</span>
                          <span className="chat-product-price">{formatPrice(p.price)}</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {sending && <div className="chat-bubble assistant typing">…</div>}
          </div>
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about merch…"
              aria-label="Chat message"
            />
            <button type="submit" disabled={sending || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
      <button
        className="chat-toggle"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '×' : 'Chat'}
      </button>
    </div>
  )
}
