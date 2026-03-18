'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../components/Auth/AuthProvider';
import { Button } from '@/components/ui/Button';
import ThemeToggle from '../components/ThemeToggle';

export default function LandingPage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  const handleGetStarted = () => {
    if (user) {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-black relative overflow-hidden">
      {/* Theme Toggle */}
      <div className="absolute top-6 right-6 z-50">
        <ThemeToggle />
      </div>

      {/* Animated Aura Background Circles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-400/20 dark:bg-blue-500/10 rounded-full blur-3xl animate-aura-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-pink-400/20 dark:bg-orange-500/10 rounded-full blur-3xl animate-aura-slow" style={{ animationDelay: '-5s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-cyan-400/15 to-purple-400/15 dark:from-blue-600/10 dark:to-cyan-600/10 rounded-full blur-3xl animate-aura-medium" style={{ animationDelay: '-10s' }}></div>
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-yellow-400/15 dark:bg-yellow-500/5 rounded-full blur-3xl animate-aura-fast" style={{ animationDelay: '-3s' }}></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-indigo-400/15 dark:bg-indigo-500/5 rounded-full blur-3xl animate-aura-pulse" style={{ animationDelay: '-7s' }}></div>
      </div>

      {/* Animated background gradient */}
      <div className="absolute inset-0 z-0 bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.15),transparent_50%)] dark:bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.1),transparent_50%)] h-[800px] w-[800px]" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="py-6 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold gradient-text">
            ✨ Todo App
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="text-gray-900 dark:text-gray-100 font-bold hover:bg-gray-100 dark:hover:bg-gray-800">
                Sign In
              </Button>
            </Link>
            <Link href="/register">
              <Button variant="primary" size="sm">
                Sign Up
              </Button>
            </Link>
          </div>
        </header>

        {/* Hero section */}
        <div className="py-20 md:py-32 text-center">
          <div className="inline-block mb-6 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-full backdrop-blur-sm">
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400">🚀 Modern Task Management</span>
          </div>

          <h2 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-gray-100 mb-6 leading-tight">
            Manage Your Tasks
            <br />
            <span className="bg-clip-text text-transparent gradient-text">
              Simply & Efficiently
            </span>
          </h2>

          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
            Stay organized and productive with our intuitive task management app.
            Create, edit, and track your tasks effortlessly in a beautiful interface with
            <span className="font-semibold text-blue-600 dark:text-blue-400"> smart AI assistance</span>.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <button
              onClick={handleGetStarted}
              disabled={loading}
              className="px-8 py-4 primary-gradient hover:opacity-90 text-white font-semibold rounded-lg transition-all duration-300 text-lg disabled:opacity-50 disabled:cursor-not-allowed glow-effect"
            >
              {loading ? 'Loading...' : '🎯 Get Started'}
            </button>
            <Link href="/login">
              <button className='bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-6 py-3 rounded-lg font-medium hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-300 shadow-md hover:shadow-lg border border-gray-200 dark:border-gray-700'>
                Sign In →
              </button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="py-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="bg-white dark:bg-gray-900 card-hover rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-800">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-600 dark:text-blue-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Easy Task Creation
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Quickly add new tasks with titles and descriptions. Stay organized effortlessly.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-900 card-hover rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-800">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-600 dark:text-blue-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Responsive Design
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Access your tasks on any device - desktop, tablet, or mobile.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-900 card-hover rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-800">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-600 dark:text-blue-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Secure & Private
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Your tasks are secure with JWT authentication. Only you can access your data.
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="py-8 text-center text-sm text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-800">
          <p>&copy; 2026 Todo App. Built with Next.js, FastAPI, and PostgreSQL.</p>
        </footer>
      </div>
    </div>
  );
}
