import { useState } from 'react'
import type { PayrollRecord } from '../api/payrollApi'
import { useDeletePayrollMutation } from '../api/payrollApi'
import PayrollUpdateForm from './PayrollUpdateForm'

interface Props {
  userId: string
  records: PayrollRecord[]
  isLoading: boolean
  isError: boolean
}

const COLUMNS = ['Payroll ID', 'Base Salary', 'Bonus', 'Deductions', 'Currency', 'Effective Date', 'Status', 'Actions']

export default function PayrollTable({ userId, records, isLoading, isError }: Props) {
  const [deletePayroll] = useDeletePayrollMutation()
  const [editTarget, setEditTarget] = useState<PayrollRecord | null>(null)
  const [confirmId, setConfirmId] = useState<string | null>(null)

  if (isLoading) return <p className="text-gray-500">Loading payroll records…</p>
  if (isError) return <p className="text-red-500">Failed to load payroll records.</p>

  return (
    <>
      <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 bg-white text-sm">
          <thead className="bg-gray-50">
            <tr>
              {COLUMNS.map((h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {records.length === 0 && (
              <tr>
                <td colSpan={COLUMNS.length} className="px-4 py-6 text-center text-gray-400">
                  No payroll records found.
                </td>
              </tr>
            )}
            {records.map((r) => (
              <tr key={r.payrollId} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 font-mono text-xs text-gray-500">{r.payrollId}</td>
                <td className="px-4 py-3 text-gray-900">{r.baseSalary}</td>
                <td className="px-4 py-3 text-gray-700">{r.bonus}</td>
                <td className="px-4 py-3 text-gray-700">{r.deductions}</td>
                <td className="px-4 py-3 text-gray-700">{r.currency}</td>
                <td className="px-4 py-3 text-gray-700">{r.effectiveDate}</td>
                <td className="px-4 py-3">
                  <span className="inline-block rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                    {r.status ?? 'ACTIVE'}
                  </span>
                </td>
                <td className="px-4 py-3 flex gap-2">
                  <button
                    onClick={() => setEditTarget(r)}
                    className="rounded bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 hover:bg-blue-100 transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => setConfirmId(r.payrollId)}
                    className="rounded bg-red-50 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-100 transition-colors"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editTarget && (
        <PayrollUpdateForm
          record={editTarget}
          userId={userId}
          onClose={() => setEditTarget(null)}
        />
      )}

      {confirmId && (
        <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-sm">
            <h2 className="text-base font-semibold text-gray-800 mb-2">Delete payroll record?</h2>
            <p className="text-sm text-gray-500 mb-6">This action cannot be undone.</p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setConfirmId(null)}
                className="rounded px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  deletePayroll({ payrollId: confirmId, userId })
                  setConfirmId(null)
                }}
                className="rounded bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
