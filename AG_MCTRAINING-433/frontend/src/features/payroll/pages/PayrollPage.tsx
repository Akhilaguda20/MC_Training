import { useState } from 'react'
import { usePayroll } from '../hooks/usePayroll'
import { useAllPayrolls } from '../hooks/useAllPayrolls'
import PayrollTable from '../components/PayrollTable'
import Pagination from '../../../shared/components/Pagination'
import { usePagination } from '../../../shared/hooks/usePagination'

const PAGE_SIZE_OPTIONS = [5, 10, 20]
type Tab = 'all' | 'by-user'

export default function PayrollPage() {
  const [tab, setTab] = useState<Tab>('all')
  const [inputValue, setInputValue] = useState('')
  const [userId, setUserId] = useState('')
  const [pageSize, setPageSize] = useState(10)

  // All payrolls
  const { records: allRecords, isLoading: allLoading, isError: allError, isFetching: allFetching } = useAllPayrolls()
  // By-user payrolls
  const { records: userRecords, isLoading: userLoading, isError: userError } = usePayroll(userId)

  const activeRecords = tab === 'all' ? allRecords : userRecords
  const isLoading = tab === 'all' ? allLoading : userLoading
  const isError = tab === 'all' ? allError : userError
  const isFetching = tab === 'all' ? allFetching : false
  const activeUserId = tab === 'all' ? '' : userId

  const { page, totalPages, totalCount, paged, setPage } = usePagination(activeRecords, pageSize)

  const tabClass = (t: Tab) =>
    `px-4 py-2 text-sm font-medium rounded-t border-b-2 transition-colors ${
      tab === t
        ? 'border-blue-600 text-blue-600 bg-white'
        : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
    }`

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-semibold text-gray-800">
          Payroll
          {isFetching && !isLoading && (
            <span className="ml-3 text-xs font-normal text-blue-500 animate-pulse">Refreshing…</span>
          )}
        </h1>
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
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200 mb-5">
        <button className={tabClass('all')} onClick={() => { setTab('all'); setPage(1) }}>
          All Payrolls
        </button>
        <button className={tabClass('by-user')} onClick={() => { setTab('by-user'); setPage(1) }}>
          By User
        </button>
      </div>

      {/* By-user search bar — only shown on By User tab */}
      {tab === 'by-user' && (
        <div className="flex gap-3 mb-5">
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { setUserId(inputValue.trim()); setPage(1) } }}
            className="w-80 rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="Enter User ID and press Search"
          />
          <button
            onClick={() => { setUserId(inputValue.trim()); setPage(1) }}
            disabled={!inputValue.trim()}
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Search
          </button>
          {userId && (
            <button
              onClick={() => { setUserId(''); setInputValue(''); setPage(1) }}
              className="rounded px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      )}

      {/* Empty state for By User tab before search */}
      {tab === 'by-user' && !userId && (
        <div className="rounded-lg border border-dashed border-gray-300 p-10 text-center text-gray-400">
          Enter a User ID above to view payroll records.
        </div>
      )}

      {/* Table — shown on All tab always, on By User tab only after search */}
      {(tab === 'all' || (tab === 'by-user' && userId)) && (
        <>
          {tab === 'by-user' && userId && (
            <p className="text-sm text-gray-500 mb-3">
              Showing records for user{' '}
              <span className="font-mono font-semibold text-gray-700">{userId}</span>
            </p>
          )}
          <PayrollTable
            userId={activeUserId}
            records={paged}
            isLoading={isLoading}
            isError={isError}
          />
          {!isLoading && !isError && totalCount > 0 && (
            <Pagination
              page={page}
              totalPages={totalPages}
              totalCount={totalCount}
              pageSize={pageSize}
              onPageChange={setPage}
              label="payroll records"
            />
          )}
        </>
      )}
    </div>
  )
}
