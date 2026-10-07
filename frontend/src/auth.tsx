import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import {
  fetchMe,
  login as apiLogin,
  logout as apiLogout,
  signup as apiSignup,
  type SignupInput,
  type User,
} from './api'

interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (input: SignupInput) => Promise<void>
  logout: () => Promise<void>
}

const TOKEN_KEY = 'cc_token'
const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [loading, setLoading] = useState(true)

  // Restore the session on first load by validating any saved token.
  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }
    fetchMe(token)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY)
        setToken(null)
      })
      .finally(() => setLoading(false))
  }, [token])

  function persist(t: string, u: User) {
    localStorage.setItem(TOKEN_KEY, t)
    setToken(t)
    setUser(u)
  }

  const value: AuthState = {
    user,
    token,
    loading,
    async login(email, password) {
      const res = await apiLogin(email, password)
      persist(res.token, res.user)
    },
    async signup(input) {
      const res = await apiSignup(input)
      persist(res.token, res.user)
    },
    async logout() {
      if (token) await apiLogout(token).catch(() => undefined)
      localStorage.removeItem(TOKEN_KEY)
      setToken(null)
      setUser(null)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
