import { configureStore } from '@reduxjs/toolkit'
import { usersApi } from '../features/users/api/usersApi'
import { payrollApi } from '../features/payroll/api/payrollApi'

export const store = configureStore({
  reducer: {
    [usersApi.reducerPath]: usersApi.reducer,
    [payrollApi.reducerPath]: payrollApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(usersApi.middleware, payrollApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
