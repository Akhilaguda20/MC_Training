import { useGetAllPayrollsQuery } from '../api/payrollApi'

export function useAllPayrolls() {
  // refetchOnMountOrArgChange: true ensures fresh data every time the Payroll page is visited
  const { data: records = [], isLoading, isError, isFetching } = useGetAllPayrollsQuery(undefined, {
    refetchOnMountOrArgChange: true,
  })
  return { records, isLoading, isError, isFetching }
}
