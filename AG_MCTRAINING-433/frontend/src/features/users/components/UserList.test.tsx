import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../../../mocks/server'
import { renderWithProviders } from '../../../test-utils'
import UserList from './UserList'
import { mockUsers } from '../../../mocks/handlers'

function setup() {
  const onEdit = vi.fn()
  renderWithProviders(
    <UserList users={mockUsers} isLoading={false} isError={false} onEdit={onEdit} />,
  )
  return { onEdit }
}

describe('UserList', () => {
  it('renders a row for each user', () => {
    setup()
    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
  })

  it('shows "No users found" when list is empty', () => {
    renderWithProviders(
      <UserList users={[]} isLoading={false} isError={false} onEdit={vi.fn()} />,
    )
    expect(screen.getByText('No users found.')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    renderWithProviders(
      <UserList users={[]} isLoading={true} isError={false} onEdit={vi.fn()} />,
    )
    expect(screen.getByText('Loading users…')).toBeInTheDocument()
  })

  it('shows error state', () => {
    renderWithProviders(
      <UserList users={[]} isLoading={false} isError={true} onEdit={vi.fn()} />,
    )
    expect(screen.getByText('Failed to load users.')).toBeInTheDocument()
  })

  it('calls onEdit with the correct user when Edit is clicked', async () => {
    const { onEdit } = setup()
    const editButtons = screen.getAllByRole('button', { name: /edit/i })
    await userEvent.click(editButtons[0])
    expect(onEdit).toHaveBeenCalledWith(mockUsers[0])
  })

  it('shows confirm dialog when Delete is clicked', async () => {
    setup()
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
    await userEvent.click(deleteButtons[0])
    expect(screen.getByText('Delete user?')).toBeInTheDocument()
  })

  it('dismisses confirm dialog on Cancel', async () => {
    setup()
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
    await userEvent.click(deleteButtons[0])
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }))
    expect(screen.queryByText('Delete user?')).not.toBeInTheDocument()
  })

  it('calls delete API and closes dialog on confirm', async () => {
    const deleted: string[] = []
    server.use(
      http.delete('http://localhost/api/v1/users/:userId', ({ params }) => {
        deleted.push(params.userId as string)
        return HttpResponse.json({ message: 'User deleted' })
      }),
    )
    setup()
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
    await userEvent.click(deleteButtons[0])
    const confirmBtn = within(screen.getByRole('dialog')).getByRole('button', { name: 'Delete' })
    await userEvent.click(confirmBtn)
    await waitFor(() => expect(deleted).toContain('u-1'))
    expect(screen.queryByText('Delete user?')).not.toBeInTheDocument()
  })
})
