import { Outlet, Link, useLocation } from 'react-router-dom'
import { TonConnectButton } from '@tonconnect/ui-react'
import { Activity, Cpu, DollarSign, User } from 'lucide-react'

export function Layout() {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/workers', label: 'Workers', icon: Cpu },
    { path: '/payouts', label: 'Payouts', icon: DollarSign },
    { path: '/account', label: 'Account', icon: User },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Cocoon GPU Pool
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <TonConnectButton />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center gap-2 py-4 px-3 border-b-2 text-sm font-medium
                    ${isActive
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            © 2025 Cocoon GPU Pool. Join our community:{' '}
            <a
              href="https://t.me/xlab_tg"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700"
            >
              @xlab_tg
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}
