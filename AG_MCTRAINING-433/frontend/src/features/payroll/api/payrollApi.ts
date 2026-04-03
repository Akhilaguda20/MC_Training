import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export interface PayrollRecord {
  payrollId: string
  userId: string
  baseSalary: string
  bonus: string
  deductions: string
  currency: string
  effectiveDate: string
  status?: string
}

export interface CreatePayrollPayload {
  userId: string
  baseSalary: string
  bonus?: string
  deductions?: string
  currency?: string
  effectiveDate: string
}

export interface UpdatePayrollPayload {
  baseSalary?: string
  bonus?: string
  deductions?: string
  currency?: string
  effectiveDate?: string
}

export const payrollApi = createApi({
  reducerPath: 'payrollApi',
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_BASE_URL ?? '',
  }),
  // Keep cache alive for 5 minutes after all subscribers unmount
  keepUnusedDataFor: 300,
  refetchOnFocus: true,
  refetchOnReconnect: true,
  tagTypes: ['Payroll'],
  endpoints: (builder) => ({
    getAllPayrolls: builder.query<PayrollRecord[], void>({
      query: () => '/payroll',
      providesTags: ['Payroll'],
    }),
    getPayrollByUser: builder.query<{ userId: string; records: PayrollRecord[] }, string>({
      query: (userId) => `/payroll/user/${userId}`,
      providesTags: (_result, _err, userId) => [{ type: 'Payroll', id: userId }],
    }),
    getPayroll: builder.query<PayrollRecord, string>({
      query: (payrollId) => `/payroll/${payrollId}`,
      providesTags: (_result, _err, id) => [{ type: 'Payroll', id }],
    }),
    createPayroll: builder.mutation<{ message: string; payrollId: string }, CreatePayrollPayload>({
      query: (body) => ({ url: '/payroll', method: 'POST', body }),
      invalidatesTags: (_result, _err, arg) => [{ type: 'Payroll', id: arg.userId }],
    }),
    updatePayroll: builder.mutation<
      { message: string },
      { payrollId: string; userId: string; body: UpdatePayrollPayload }
    >({
      query: ({ payrollId, body }) => ({ url: `/payroll/${payrollId}`, method: 'PUT', body }),
      invalidatesTags: (_result, _err, arg) => ['Payroll', { type: 'Payroll', id: arg.userId }],
    }),
    deletePayroll: builder.mutation<{ message: string }, { payrollId: string; userId: string }>({
      query: ({ payrollId }) => ({ url: `/payroll/${payrollId}`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, arg) => ['Payroll', { type: 'Payroll', id: arg.userId }],
    }),
  }),
})

export const {
  useGetAllPayrollsQuery,
  useGetPayrollByUserQuery,
  useGetPayrollQuery,
  useCreatePayrollMutation,
  useUpdatePayrollMutation,
  useDeletePayrollMutation,
} = payrollApi
