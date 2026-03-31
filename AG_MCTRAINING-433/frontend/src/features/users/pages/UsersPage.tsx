import { useState } from 'react'
import type { User } from '../api/usersApi'
import { useUsers } from '../hooks/useUsers'
import UserList from '../components/UserList'
import UserForm from '../components/UserForm'
import Pagination from '../../../shared/components/Pagination'
import { usePagination } from '../../../shared/hooks/usePagination'

const PAGE_SIZE_OPTIONS = [5, 10, 20, 50]

export default function UsersPage() {
  const { users, isLoading, isError, isFetching } = useUsers()
  const [formOpen, setFormOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<User | undefined>(undefined)
  const [pageSize, setPageSize] = useState(10)

  const { page, totalPages, totalCount, paged, setPage } = usePagination(users, pageSize)

  function openCreate() {
    setEditTarget(undefined)
    setFormOpen(true)
  }

  function openEdit(user: User) {
    setEditTarget(user)
    setFormOpen(true)
  }

  function closeForm() {
    setFormOpen(false)
    setEditTarget(undefined)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-semibold text-gray-800">
          User Management
          {isFetching && !isLoading && (
            <span className="ml-3 text-xs font-normal text-blue-500 animate-pulse">Refreshing…</span>
          )}
        </h1>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            Per page:
            <select
              value={pageSize}
              onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}
              className="rounded border border-gray-300 px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {PAGE_SIZE_OPTIONS.map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
          <button
            onClick={openCreate}
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            + New User
          </button>
        </div>
      </div>

      <UserList users={paged} isLoading={isLoading} isError={isError} onEdit={openEdit} />

      {!isLoading && !isError && totalCount > 0 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          totalCount={totalCount}
          pageSize={pageSize}
          onPageChange={setPage}
          label="users"
        />
      )}

      {formOpen && <UserForm initialValues={editTarget} onClose={closeForm} />}
    </div>
  )
}

