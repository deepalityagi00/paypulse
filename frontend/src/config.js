// Central place for all backend-facing configuration so the Django endpoints
// can be re-pointed from a single file / via env vars.

// Empty string => same-origin (dev proxy or same-host prod deploy).
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export const GMAIL_AUTH_PATH =
  import.meta.env.VITE_GMAIL_AUTH_PATH ?? '/gmail/auth/'

export const STRIPE_CONNECT_PATH =
  import.meta.env.VITE_STRIPE_CONNECT_PATH ?? '/stripe/connect/'

/** Build an absolute backend URL from a path. */
export const apiUrl = (path) => `${API_BASE_URL}${path}`
