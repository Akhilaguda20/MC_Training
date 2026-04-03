import { type ReactNode } from 'react'
import { render } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter } from 'react-router-dom'
import { usersApi } from './features/users/api/usersApi'
import { payrollApi } from './features/payroll/api/payrollApi'

function makeTestStore() {
  return configureStore({
    reducer: {
      [usersApi.reducerPath]: usersApi.reducer,
      [payrollApi.reducerPath]: payrollApi.reducer,
    },
    middleware: (getDefault) =>
      getDefault().concat(usersApi.middleware, payrollApi.middleware),
  })
}

export function renderWithProviders(
  ui: ReactNode,
  { initialEntries = ['/'] }: { initialEntries?: string[] } = {},
) {
  const store = makeTestStore()
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={initialEntries}>{ui}</MemoryRouter>
    </Provider>,
  )
}
