import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout() {
  return (
    <div className="flex h-screen bg-secondary-50">
      {/* Sidebar */}
      <aside className="w-64 bg-secondary-900 text-white flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-secondary-800">
          <h1 className="text-xl font-bold">TradeFinance</h1>
        </div>
        <Sidebar />
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
