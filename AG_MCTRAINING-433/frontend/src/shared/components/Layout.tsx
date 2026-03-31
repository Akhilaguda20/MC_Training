import { Suspense } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

export default function Layout() {
  const navClass = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded text-sm font-medium transition-colors ${
      isActive
        ? 'bg-blue-600 text-white'
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
    }`

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-4 shadow-sm">
        <span className="text-lg font-semibold text-gray-800 mr-6">MC Training</span>
        <NavLink to="/users" className={navClass}>
          Users
        </NavLink>
        <NavLink to="/payroll" className={navClass}>
          Payroll
        </NavLink>
      </nav>
      <main className="p-6">
        <Suspense fallback={<div className="text-gray-500">Loading…</div>}>
          <Outlet />
        </Suspense>
      </main>
    </div>
  )
}
