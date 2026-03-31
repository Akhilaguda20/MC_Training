import { lazy } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Layout from '../shared/components/Layout'

const UsersPage = lazy(() => import('../features/users/pages/UsersPage'))
const PayrollPage = lazy(() => import('../features/payroll/pages/PayrollPage'))

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <UsersPage /> },
      { path: 'users', element: <UsersPage /> },
      { path: 'payroll', element: <PayrollPage /> },
    ],
  },
])
