import { Link } from 'react-router-dom'
import { Plus } from 'lucide-react'

export default function LCList() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-secondary-900">Letter of Credit</h1>
        <Link to="/lc/create" className="btn-primary">
          <Plus className="h-5 w-5 mr-2" />
          Create LC
        </Link>
      </div>
      <div className="card">
        <div className="card-body">
          <p className="text-secondary-500">LC List will be displayed here</p>
        </div>
      </div>
    </div>
  )
}
