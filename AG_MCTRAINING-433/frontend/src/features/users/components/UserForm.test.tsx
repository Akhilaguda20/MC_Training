import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../../../mocks/server'
import { renderWithProviders } from '../../../test-utils'
import UserForm from './UserForm'

describe('UserForm — create mode', () => {
  it('renders create form title', () => {
    renderWithProviders(<UserForm onClose={vi.fn()} />)
    expect(screen.getByText('Create User')).toBeInTheDocument()
  })

  it('shows validation errors when submitted empty', async () => {
    renderWithProviders(<UserForm onClose={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /create user/i }))
    expect(await screen.findByText('Name is required.')).toBeInTheDocument()
    expect(screen.getByText('Email is required.')).toBeInTheDocument()
  })

  it('shows email format error for invalid email', async () => {
    renderWithProviders(<UserForm onClose={vi.fn()} />)
    await userEvent.type(screen.getByLabelText(/name/i), 'Alice')
    await userEvent.type(screen.getByLabelText(/email/i), 'not-an-email')
    await userEvent.click(screen.getByRole('button', { name: /create user/i }))
    expect(await screen.findByText('Enter a valid email address.')).toBeInTheDocument()
  })

  it('calls create API and invokes onClose on successful submit', async () => {
    const posted: unknown[] = []
    server.use(
      http.post('http://localhost/api/v1/users', async ({ request }) => {
        posted.push(await request.json())
        return HttpResponse.json({ message: 'User created', userId: 'u-new' }, { status: 201 })
      }),
    )
    const onClose = vi.fn()
    renderWithProviders(<UserForm onClose={onClose} />)
    await userEvent.type(screen.getByLabelText(/name/i), 'Alice')
    await userEvent.type(screen.getByLabelText(/email/i), 'alice@example.com')
    await userEvent.click(screen.getByRole('button', { name: /create user/i }))
    await waitFor(() => expect(onClose).toHaveBeenCalledOnce())
    expect(posted[0]).toMatchObject({ name: 'Alice', email: 'alice@example.com' })
  })
})

describe('UserForm — edit mode', () => {
  const existing = { userId: 'u-1', name: 'Alice', email: 'alice@example.com', status: 'CREATED' }

  it('renders edit form title and pre-fills fields', () => {
    renderWithProviders(<UserForm initialValues={existing} onClose={vi.fn()} />)
    expect(screen.getByText('Edit User')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Alice')).toBeInTheDocument()
    expect(screen.getByDisplayValue('alice@example.com')).toBeInTheDocument()
  })

  it('calls update API and invokes onClose on submit', async () => {
    const updated: unknown[] = []
    server.use(
      http.put('http://localhost/api/v1/users/:userId', async ({ request }) => {
        updated.push(await request.json())
        return HttpResponse.json({ message: 'Event sent' })
      }),
    )
    const onClose = vi.fn()
    renderWithProviders(<UserForm initialValues={existing} onClose={onClose} />)
    const nameInput = screen.getByDisplayValue('Alice')
    await userEvent.clear(nameInput)
    await userEvent.type(nameInput, 'Alice Updated')
    await userEvent.click(screen.getByRole('button', { name: /save changes/i }))
    await waitFor(() => expect(onClose).toHaveBeenCalledOnce())
    expect(updated[0]).toMatchObject({ name: 'Alice Updated' })
  })

  it('calls onClose when Cancel is clicked', async () => {
    const onClose = vi.fn()
    renderWithProviders(<UserForm initialValues={existing} onClose={onClose} />)
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }))
    expect(onClose).toHaveBeenCalledOnce()
  })
})
