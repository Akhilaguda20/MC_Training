import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../../../mocks/server'
import { renderWithProviders } from '../../../test-utils'
import PayrollTable from './PayrollTable'
import { mockPayroll } from '../../../mocks/handlers'

function setup() {
  renderWithProviders(
    <PayrollTable
      userId="u-1"
      records={mockPayroll}
      isLoading={false}
      isError={false}
    />,
  )
}

describe('PayrollTable', () => {
  it('renders a row for each payroll record', () => {
    setup()
    expect(screen.getByText('p-1')).toBeInTheDocument()
    expect(screen.getByText('75000')).toBeInTheDocument()
  })

  it('shows "No payroll records found" when list is empty', () => {
    renderWithProviders(
      <PayrollTable userId="u-1" records={[]} isLoading={false} isError={false} />,
    )
    expect(screen.getByText('No payroll records found.')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    renderWithProviders(
      <PayrollTable userId="u-1" records={[]} isLoading={true} isError={false} />,
    )
    expect(screen.getByText('Loading payroll records…')).toBeInTheDocument()
  })

  it('shows error state', () => {
    renderWithProviders(
      <PayrollTable userId="u-1" records={[]} isLoading={false} isError={true} />,
    )
    expect(screen.getByText('Failed to load payroll records.')).toBeInTheDocument()
  })

  it('opens edit form when Edit is clicked', async () => {
    setup()
    await userEvent.click(screen.getAllByRole('button', { name: /edit/i })[0])
    expect(screen.getByText('Edit Payroll Record')).toBeInTheDocument()
  })

  it('shows confirm dialog when Delete is clicked', async () => {
    setup()
    await userEvent.click(screen.getAllByRole('button', { name: /delete/i })[0])
    expect(screen.getByText('Delete payroll record?')).toBeInTheDocument()
  })

  it('cancels delete dialog', async () => {
    setup()
    await userEvent.click(screen.getAllByRole('button', { name: /delete/i })[0])
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }))
    expect(screen.queryByText('Delete payroll record?')).not.toBeInTheDocument()
  })

  it('calls delete API and closes dialog on confirm', async () => {
    const deleted: string[] = []
    server.use(
      http.delete('http://localhost/api/v1/payroll/:payrollId', ({ params }) => {
        deleted.push(params.payrollId as string)
        return HttpResponse.json({ message: 'Payroll record deleted' })
      }),
    )
    setup()
    await userEvent.click(screen.getAllByRole('button', { name: /delete/i })[0])
    const confirmBtn = within(screen.getByRole('dialog')).getByRole('button', { name: 'Delete' })
    await userEvent.click(confirmBtn)
    await waitFor(() => expect(deleted).toContain('p-1'))
    expect(screen.queryByText('Delete payroll record?')).not.toBeInTheDocument()
  })
})
