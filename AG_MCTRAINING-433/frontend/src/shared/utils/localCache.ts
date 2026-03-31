/**
 * Lightweight localStorage cache for RTK Query responses.
 *
 * On page reload RTK Query starts fresh. This module:
 *  1. Saves the users list to localStorage whenever RTK Query fetches it.
 *  2. Pre-populates `initialEntries` so the UI shows stale data instantly
 *     while the real fetch completes in the background.
 *
 * Kept deliberately simple — no versioning, TTL of 10 minutes.
 */

const USERS_KEY = 'mc_cache_users'
const TTL_MS = 10 * 60 * 1000 // 10 minutes

interface CacheEntry<T> {
  data: T
  savedAt: number
}

export function saveToCache<T>(key: string, data: T): void {
  try {
    const entry: CacheEntry<T> = { data, savedAt: Date.now() }
    localStorage.setItem(key, JSON.stringify(entry))
  } catch {
    // localStorage may be full or unavailable — fail silently
  }
}

export function loadFromCache<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return null
    const entry: CacheEntry<T> = JSON.parse(raw)
    if (Date.now() - entry.savedAt > TTL_MS) {
      localStorage.removeItem(key)
      return null
    }
    return entry.data
  } catch {
    return null
  }
}

export function clearCache(key: string): void {
  localStorage.removeItem(key)
}

export { USERS_KEY }
