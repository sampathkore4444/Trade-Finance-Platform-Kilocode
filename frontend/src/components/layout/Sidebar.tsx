import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Shield,
  Receipt,
  FileCheck,
  DollarSign,
  AlertTriangle,
  ClipboardCheck,
  BarChart3,
  Settings,
  Users,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Letter of Credit', href: '/lc', icon: FileText },
  { name: 'Bank Guarantee', href: '/guarantee', icon: Shield },
  { name: 'Collection', href: '/collection', icon: Receipt },
  { name: 'Invoice Finance', href: '/invoice', icon: FileCheck },
  { name: 'Trade Loan', href: '/loan', icon: DollarSign },
  { name: 'Risk Management', href: '/risk', icon: AlertTriangle },
  { name: 'Compliance', href: '/compliance', icon: ClipboardCheck },
  { name: 'Reports', href: '/reports', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Users', href: '/admin/users', icon: Users },
]

export default function Sidebar() {
  return (
    <nav className="flex-1 overflow-y-auto py-4">
      <ul className="space-y-1 px-2">
        {navigation.map((item) => (
          <li key={item.name}>
            <NavLink
              to={item.href}
              className={({ isActive }) =>
                `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-secondary-300 hover:bg-secondary-800 hover:text-white'
                }`
              }
            >
              <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
              {item.name}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
