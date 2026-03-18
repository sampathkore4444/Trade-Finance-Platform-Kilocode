import { useState, useEffect } from 'react'
import { Plus, Search, Filter, MoreVertical, Edit, Trash2, User, Mail, Building2, Shield, RefreshCw, Loader2 } from 'lucide-react'
import api from '@/api/axios'

interface UserData {
  id: number
  name: string
  email: string
  role: string
  department: string
  status: string
  lastLogin: string
}

const roles = ['Administrator', 'Credit Officer', 'Relationship Manager', 'Compliance Officer', 'Operations', 'Viewer']
const departments = ['Operations', 'Credit', 'Corporate Banking', 'Compliance', 'Risk', 'IT']

export default function Users() {
  const [isLoading, setIsLoading] = useState(true)
  const [users, setUsers] = useState<UserData[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchUsers()
  }, [searchTerm, roleFilter])

  const fetchUsers = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (searchTerm) params.append('search', searchTerm)
      // Note: Role filtering would need backend support
      
      const response = await api.get(`/users/?${params.toString()}`)
      
      if (response.data && response.data.items) {
        const userList = response.data.items.map((user: any) => ({
          id: user.id,
          name: user.full_name || user.email?.split('@')[0] || 'Unknown',
          email: user.email || '',
          role: user.role || 'Viewer',
          department: user.department || 'Operations',
          status: user.is_active ? 'active' : 'inactive',
          lastLogin: user.last_login ? new Date(user.last_login).toLocaleString() : 'Never',
        }))
        setUsers(userList)
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Stats
  const totalUsers = users.length
  const activeUsers = users.filter(u => u.status === 'active').length
  const adminUsers = users.filter(u => u.role === 'Administrator').length

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">User Management</h1>
          <p className="text-sm text-secondary-500 mt-1">Manage system users and permissions</p>
        </div>
        <button className="btn-primary">
          <Plus className="h-5 w-5 mr-2" /> Add User
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg mr-4">
              <User className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Total Users</p>
              <p className="text-xl font-semibold text-secondary-900">{totalUsers}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-green-100 rounded-lg mr-4">
              <Shield className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Active Users</p>
              <p className="text-xl font-semibold text-secondary-900">{activeUsers}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg mr-4">
              <Building2 className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Departments</p>
              <p className="text-xl font-semibold text-secondary-900">{departments.length}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg mr-4">
              <Shield className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Administrators</p>
              <p className="text-xl font-semibold text-secondary-900">{adminUsers}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-body">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
                <input
                  type="text"
                  placeholder="Search users..."
                  className="input pl-10 w-full md:w-64"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <select
                className="input w-40"
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
              >
                <option value="">All Roles</option>
                {roles.map((role) => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
              <button
                className="btn-outline"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-2" /> More Filters
              </button>
              <button
                className="btn-outline"
                onClick={fetchUsers}
              >
                <RefreshCw className="h-4 w-4 mr-2" /> Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {users.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Status</th>
                  <th>Last Login</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center mr-3">
                          <span className="text-primary-600 font-medium">
                            {user.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium text-secondary-900">{user.name}</p>
                          <p className="text-sm text-secondary-500">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-info">{user.role}</span>
                    </td>
                    <td>{user.department}</td>
                    <td>
                      <span className={`badge ${user.status === 'active' ? 'badge-success' : 'badge-secondary'}`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="text-secondary-500">{user.lastLogin}</td>
                    <td>
                      <div className="flex items-center space-x-2">
                        <button className="text-secondary-400 hover:text-primary-600">
                          <Edit className="h-4 w-4" />
                        </button>
                        <button className="text-secondary-400 hover:text-red-600">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-8 text-secondary-500">
              No users found
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
