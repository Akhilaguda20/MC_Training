import { http, HttpResponse } from 'msw'
import type { User } from '../features/users/api/usersApi'
import type { PayrollRecord } from '../features/payroll/api/payrollApi'

const BASE = 'http://localhost/api/v1'

export const mockUsers: User[] = [
  { userId: 'u-1', name: 'Alice', email: 'alice@example.com', status: 'CREATED' },
  { userId: 'u-2', name: 'Bob', email: 'bob@example.com', status: 'CREATED' },
]

export const mockPayroll: PayrollRecord[] = [
  {
    payrollId: 'p-1',
    userId: 'u-1',
    baseSalary: '75000',
    bonus: '5000',
    deductions: '1200',
    currency: 'USD',
    effectiveDate: '2026-01-01',
    status: 'ACTIVE',
  },
]

export const handlers = [
  // Users
  http.get(`${BASE}/users`, () => HttpResponse.json(mockUsers)),
  http.get(`${BASE}/users/:userId`, ({ params }) => {
    const user = mockUsers.find((u) => u.userId === params.userId)
    return user ? HttpResponse.json(user) : new HttpResponse(null, { status: 404 })
  }),
  http.post(`${BASE}/users`, () =>
    HttpResponse.json({ message: 'User created', userId: 'u-new' }, { status: 201 }),
  ),
  http.put(`${BASE}/users/:userId`, () =>
    HttpResponse.json({ message: 'Event sent' }),
  ),
  http.delete(`${BASE}/users/:userId`, () =>
    HttpResponse.json({ message: 'User deleted' }),
  ),

  // Payroll
  http.get(`${BASE}/payroll`, () => HttpResponse.json(mockPayroll)),
  http.get(`${BASE}/payroll/user/:userId`, ({ params }) =>
    HttpResponse.json({
      userId: params.userId,
      records: mockPayroll.filter((r) => r.userId === params.userId),
    }),
  ),
  http.get(`${BASE}/payroll/:payrollId`, ({ params }) => {
    const record = mockPayroll.find((r) => r.payrollId === params.payrollId)
    return record ? HttpResponse.json(record) : new HttpResponse(null, { status: 404 })
  }),
  http.put(`${BASE}/payroll/:payrollId`, () =>
    HttpResponse.json({ message: 'Payroll record updated' }),
  ),
  http.post(`${BASE}/payroll`, () =>
    HttpResponse.json({ message: 'Payroll record created', payrollId: 'p-new' }, { status: 201 }),
  ),
  http.delete(`${BASE}/payroll/:payrollId`, () =>
    HttpResponse.json({ message: 'Payroll record deleted' }),
  ),
]
