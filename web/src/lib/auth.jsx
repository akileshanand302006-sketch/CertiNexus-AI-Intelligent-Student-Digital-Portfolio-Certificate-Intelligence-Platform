/**
 * CertiNexus AI — Auth Context
 */

import { createContext, useContext, useState, useEffect } from 'react'
import api from './api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = api.getToken()
    if (token) {
      api.getMe()
        .then(setUser)
        .catch(() => { api.clearTokens() })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    await api.login({ email, password })
    const user = await api.getMe()
    setUser(user)
    return user
  }

  const register = async (data) => {
    await api.register(data)
    const user = await api.getMe()
    setUser(user)
    return user
  }

  const logout = () => {
    api.logout()
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
