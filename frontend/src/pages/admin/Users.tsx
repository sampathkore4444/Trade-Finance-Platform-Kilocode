import { useState } from 'react'
import { Plus, Search, Filter, MoreVertical, Edit, Trash2, User, Mail, Building2, Shield, RefreshCw } from 'lucide-react'

const users = [
  { id: 1, name: 'John Smith', email: 'john.smith@bank.com', role: 'Administrator', department: 'Operations', status: 'active', lastLogin: '2024-01-15 09:30' },
  { id: 2, name: 'Jane Doe', email: 'jane.doe@bank.com', role: 'Credit Officer', department: 'Credit', status: 'active', lastLogin: '2024-01-15 08:45' },
  { id: 3, name: 'Mike Johnson', email: 'mike.j@bank.com', role: 'Relationship Manager', department: 'Corporate Banking', status: 'active', lastLogin: '2024-01-14 16:20' },
  { id: 4, name: 'Sarah Wilson', email: 'sarah.w@bank.com', role: 'Compliance Officer', department: 'Compliance', status: 'active', lastLogin: '2024-01-15 10:00' },
  { id: 5, name: 'Tom Brown', email: 'tom.brown@bank.com', role: 'Operations', department: 'Operations', status: 'inactive', lastLogin: '2024-01-10 14:30' },
]

const roles = ['Administrator', 'Credit Officer', 'Relationship Manager', 'Compliance Officer', 'Operations', 'Viewer']
const departments = ['Operations', 'Credit', 'Corporate Banking', 'Compliance', 'Risk', 'IT']

export default function Users() {
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [showFilters, setShowFilters] = useState(false)

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
              <p className="text-xl font-semibold text-secondary-900">{users.length}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-green-100 rounded-lg mr-4">
              <Shield className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Active</p>
              <p className="text-xl font-semibold text-secondary-900">{users.filter(u => u.status === 'active').length}</p>
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
              <p className="text-sm text-secondary-500">Roles</p>
              <p className="text-xl font-semibold text-secondary-900">{roles.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="card-body">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search users..."
                className="input pl-10"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn ${showFilters ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Filter className="w-4 h-4 mr-2" /> Filters
            </button>
            <button className="btn-outline">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-secondary-200 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Role</label>
                <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)} className="input">
                  <option value="">All Roles</option>
                  {roles.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div className="flex items-end">
                <button onClick={() => { setSearchTerm(''); setRoleFilter('') }} className="btn-outline w-full">Clear</button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Users Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Role</th>
                <th>Department</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users
                .filter(u => searchTerm === '' || u.name.toLowerCase().includes(searchTerm.toLowerCase()) || u.email.toLowerCase().includes(searchTerm.toLowerCase()))
                .filter(u => roleFilter === '' || u.role === roleFilter)
                .map((user) => (
                <tr key={user.id} className="hover:bg-secondary-50">
                  <td>
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                        <span className="text-sm font-medium text-primary-600">{user.name.charAt(0)}</span>
                      </div>
                      <span className="font-medium">{user.name}</span>
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center">
                      <Mail className="w-4 h-4 text-secondary-400 mr-2" />
                      {user.email}
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-secondary">{user.role}</span>
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
                      <button className="p-1 text-secondary-400 hover:text-primary-600">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="p-1 text-secondary-400 hover:text-red-600">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
