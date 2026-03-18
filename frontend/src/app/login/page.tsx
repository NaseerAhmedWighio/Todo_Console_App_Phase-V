'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../components/Auth/AuthProvider'
import ThemeToggle from '../../components/ThemeToggle'
import { validateEmail, validatePassword, loginSchema } from '../../lib/validations/auth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isResending, setIsResending] = useState(false)
  const router = useRouter()
  const { login, resendVerification } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate using Zod schema
    const validation = loginSchema.safeParse({ email, password })
    if (!validation.success) {
      setError(validation.error.issues[0].message)
      return
    }
    
    try {
      await login(email, password)
      router.push('/dashboard')
      router.refresh()
    } catch (err: any) {
      setError(err.message || 'Invalid email or password')
      console.error(err)
    }
  }

  const handleResendVerification = async () => {
    if (!email) {
      setError('Please enter your email first')
      return
    }
    
    setIsResending(true)
    try {
      await resendVerification(email)
      setError('Verification email sent! Please check your inbox.')
    } catch (err: any) {
      setError(err.message || 'Failed to resend verification email')
    } finally {
      setIsResending(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-[#0A0A0A] relative overflow-hidden">
      {/* Animated Aura Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/25 dark:bg-blue-500/10 rounded-full blur-3xl animate-aura-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-400/25 dark:bg-orange-500/10 rounded-full blur-3xl animate-aura-slow" style={{ animationDelay: '-5s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-cyan-400/20 to-purple-400/20 dark:from-blue-600/10 dark:to-cyan-600/10 rounded-full blur-3xl animate-aura-medium" style={{ animationDelay: '-10s' }}></div>
      </div>

      <div className="w-full max-w-md p-8 space-y-8 bg-white dark:bg-[#151515] backdrop-blur-sm rounded-lg shadow-xl relative z-10 border border-[#EBBDC0] dark:border-gray-700">
        <div className="absolute top-4 right-4 z-20">
          <ThemeToggle />
        </div>
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Login</h2>
          <p className="mt-2 text-gray-600 dark:text-gray-300">Sign in to your account</p>
        </div>
        {error && (
          <div className="text-red-500 dark:text-red-400 text-center">
            {error}
            {error.includes('not verified') && (
              <div className="mt-3">
                <button
                  onClick={handleResendVerification}
                  disabled={isResending}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50"
                >
                  {isResending ? 'Sending...' : 'Click here to resend verification email'}
                </button>
              </div>
            )}
          </div>
        )}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#151515] text-gray-900 dark:text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                placeholder="your@email.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#151515] text-gray-900 dark:text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white primary-gradient hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300 glow-effect"
            >
              Sign in
            </button>
          </div>
        </form>
        <div className="text-center text-sm text-gray-600 dark:text-gray-400">
          Don't have an account?{' '}
          <a href="/register" className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 transition-colors duration-300">
            Register here
          </a>
        </div>
      </div>
    </div>
  )
}
