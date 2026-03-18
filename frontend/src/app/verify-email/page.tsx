'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '../../components/Auth/AuthProvider'
import ThemeToggle from '../../components/ThemeToggle'

export default function VerifyEmailPage() {
  const [verificationStatus, setVerificationStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [message, setMessage] = useState('')
  const [isResending, setIsResending] = useState(false)
  const [resendEmail, setResendEmail] = useState('')
  const searchParams = useSearchParams()
  const router = useRouter()
  const { getToken } = useAuth()

  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      verifyEmail(token)
    } else {
      setVerificationStatus('error')
      setMessage('No verification token provided')
    }
  }, [searchParams])

  const verifyEmail = async (token: string) => {
    try {
      const response = await fetch('/api/v1/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setVerificationStatus('success')
        setMessage('Email verified successfully! Redirecting to dashboard...')
        
        // Store the new token
        if (data.data?.token) {
          localStorage.setItem('token', data.data.token)
          if (data.data.user) {
            localStorage.setItem('user', JSON.stringify(data.data.user))
          }
        }

        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
          router.push('/dashboard')
        }, 2000)
      } else {
        setVerificationStatus('error')
        setMessage(data.detail || 'Verification failed')
      }
    } catch (error: any) {
      setVerificationStatus('error')
      setMessage('Verification failed. Please try again.')
      console.error('Verification error:', error)
    }
  }

  const handleResendVerification = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!resendEmail) return

    setIsResending(true)
    try {
      const response = await fetch(`/api/v1/auth/resend-verification?email=${encodeURIComponent(resendEmail)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setMessage(data.message || 'Verification email resent! Please check your inbox.')
        setResendEmail('')
      } else {
        setMessage(data.detail || 'Failed to resend verification email')
      }
    } catch (error: any) {
      setMessage('Failed to resend verification email. Please try again.')
      console.error('Resend error:', error)
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
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            {verificationStatus === 'verifying' && 'Verify Email'}
            {verificationStatus === 'success' && 'Email Verified!'}
            {verificationStatus === 'error' && 'Verification Failed'}
          </h2>
        </div>

        {verificationStatus === 'verifying' && (
          <div className="space-y-4 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-600 dark:text-gray-300">Verifying your email address...</p>
          </div>
        )}

        {verificationStatus === 'success' && (
          <div className="space-y-4 text-center">
            <div className="text-green-500 text-6xl">✓</div>
            <p className="text-gray-600 dark:text-gray-300">{message}</p>
            <button
              onClick={() => router.push('/dashboard')}
              className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white primary-gradient hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300"
            >
              Go to Dashboard
            </button>
          </div>
        )}

        {verificationStatus === 'error' && (
          <div className="space-y-4 text-center">
            <div className="text-red-500 text-6xl">✗</div>
            <p className="text-gray-600 dark:text-gray-300">{message}</p>
            
            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                Need to resend verification email?
              </h3>
              <form onSubmit={handleResendVerification} className="space-y-3">
                <input
                  type="email"
                  value={resendEmail}
                  onChange={(e) => setResendEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#151515] text-gray-900 dark:text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                />
                <button
                  type="submit"
                  disabled={isResending}
                  className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white primary-gradient hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isResending ? 'Sending...' : 'Resend Verification Email'}
                </button>
              </form>
            </div>

            <button
              onClick={() => router.push('/login')}
              className="w-full py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-[#151515] hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300"
            >
              Back to Login
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
