export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  image_url: string
  price: number
  total_stock: number
  in_stock: boolean
}

export interface SizeStock {
  size: string
  quantity: number
}

export interface ProductDetail extends Product {
  sizes: SizeStock[]
}

export interface ChatProduct {
  product_id: string
  name: string
  garment_type: string
  price: number
  image_url: string
  description: string
}

export interface ChatResponse {
  reply: string
  products: ChatProduct[]
}

export interface User {
  id: number
  first_name: string
  last_name: string
  email: string
}

export interface AuthResponse {
  token: string
  user: User
}

export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init)
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (typeof body?.detail === 'string') detail = body.detail
      else if (Array.isArray(body?.detail) && body.detail[0]?.msg) detail = body.detail[0].msg
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(detail)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

function authHeaders(token: string | null): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const getProducts = () => request<Product[]>('/api/products')

export const getProduct = (id: string) =>
  request<ProductDetail>(`/api/products/${encodeURIComponent(id)}`)

export interface SignupInput {
  first_name: string
  last_name: string
  email: string
  password: string
}

export const signup = (input: SignupInput) =>
  request<AuthResponse>('/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })

export const login = (email: string, password: string) =>
  request<AuthResponse>('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

export const logout = (token: string) =>
  request<void>('/api/auth/logout', { method: 'POST', headers: authHeaders(token) })

export const fetchMe = (token: string) =>
  request<User>('/api/auth/me', { headers: authHeaders(token) })

export interface ChatHistoryMessage {
  role: 'user' | 'assistant'
  content: string
  products: ChatProduct[]
}

export const sendChat = (
  message: string,
  opts: { token?: string | null; currentProductId?: string | null } = {},
) =>
  request<ChatResponse>('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(opts.token ?? null),
    },
    body: JSON.stringify({ message, current_product_id: opts.currentProductId ?? null }),
  })

export const getChatHistory = (token: string) =>
  request<{ messages: ChatHistoryMessage[] }>('/api/chat/history', {
    headers: authHeaders(token),
  })

export const formatPrice = (price: number) => `$${price.toFixed(2)}`

// Bump this when the product images change so browsers fetch the fresh (white-bg)
// versions instead of a stale cached copy at the same URL.
const IMG_VERSION = 'w4'
export const imageUrl = (url: string) =>
  `${url}${url.includes('?') ? '&' : '?'}v=${IMG_VERSION}`
