import { useState, type FormEvent } from 'react'
import type { PayrollRecord } from '../api/payrollApi'
import { useUpdatePayrollMutation } from '../api/payrollApi'

interface Props {
  record: PayrollRecord
  userId: string
  onClose: () => void
}

export default function PayrollUpdateForm({ record, userId, onClose }: Props) {
  const [values, setValues] = useState({
    baseSalary: record.baseSalary,
    bonus: record.bonus,
    deductions: record.deductions,
    currency: record.currency,
    effectiveDate: record.effectiveDate,
  })
  const [updatePayroll, { isLoading }] = useUpdatePayrollMutation()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    await updatePayroll({ payrollId: record.payrollId, userId, body: values })
    onClose()
  }

  const field = (key: keyof typeof values, label: string, type = 'text') => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor={key}>
        {label}
      </label>
      <input
        id={key}
        type={type}
        value={values[key]}
        onChange={(e) => setValues((p) => ({ ...p, [key]: e.target.value }))}
        className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
    </div>
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 className="text-base font-semibold text-gray-800 mb-4">Edit Payroll Record</h2>

        <form onSubmit={handleSubmit} noValidate>
          {field('baseSalary', 'Base Salary')}
          {field('bonus', 'Bonus')}
          {field('deductions', 'Deductions')}
          {field('currency', 'Currency')}
          {field('effectiveDate', 'Effective Date', 'date')}

          <div className="flex justify-end gap-3 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Saving…' : 'Save changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
