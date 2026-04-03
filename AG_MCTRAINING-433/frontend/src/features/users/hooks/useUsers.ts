import { useEffect } from 'react'
import { useGetUsersQuery } from '../api/usersApi'
import type { User } from '../api/usersApi'
import { saveToCache, loadFromCache, USERS_KEY } from '../../../shared/utils/localCache'

export function useUsers() {
  // Load stale data from localStorage so the table renders immediately on page reload
  const cachedUsers = loadFromCache<User[]>(USERS_KEY) ?? []

  const { data, isLoading, isError, isFetching, refetch } = useGetUsersQuery(undefined, {
    refetchOnMountOrArgChange: true,
  })

  // Save fresh data to localStorage every time the API returns successfully
  useEffect(() => {
    if (data) saveToCache(USERS_KEY, data)
  }, [data])

  // Show live data when available, fall back to cached data while loading
  const users = data ?? cachedUsers

  return { users, isLoading: isLoading && cachedUsers.length === 0, isFetching, isError, refetch }
}
