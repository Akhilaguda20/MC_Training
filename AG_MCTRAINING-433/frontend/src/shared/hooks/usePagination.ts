import { useState } from 'react'

export function usePagination<T>(items: T[], pageSize: number) {
  const [page, setPage] = useState(1)
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize))
  // Clamp page if items shrink (e.g. after delete)
  const safePage = Math.min(page, totalPages)
  const paged = items.slice((safePage - 1) * pageSize, safePage * pageSize)

  return {
    page: safePage,
    totalPages,
    totalCount: items.length,
    paged,
    setPage,
  }
}
