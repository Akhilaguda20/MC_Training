import { useGetPayrollByUserQuery } from '../api/payrollApi'

export function usePayroll(userId: string) {
  const { data, isLoading, isError, isFetching } = useGetPayrollByUserQuery(userId, {
    skip: !userId.trim(),
  })
  return {
    records: data?.records ?? [],
    isLoading,
    isFetching,
    isError,
  }
}
