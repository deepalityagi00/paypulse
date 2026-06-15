import { apiUrl, GMAIL_AUTH_PATH, STRIPE_CONNECT_PATH } from '../config'

/**
 * Read the Django CSRF token from the `csrftoken` cookie so authenticated
 * POSTs pass CsrfViewMiddleware. Returns null when the cookie is absent.
 */
export function getCsrfToken() {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : null
}

/**
 * Start the Gmail OAuth 2.0 flow. The backend (GmailAuthInitView) responds
 * with a redirect to Google's consent screen, so we navigate the whole window
 * rather than fetching — the browser needs to follow the redirect chain.
 *
 * An optional `email` is forwarded as `login_hint` so Google can pre-select
 * the account the user typed in the sign-in popup.
 */
export function startGmailAuth(email) {
  const base = apiUrl(GMAIL_AUTH_PATH)
  const url =
    email && typeof email === 'string'
      ? `${base}?login_hint=${encodeURIComponent(email)}`
      : base
  window.location.assign(url)
}

/**
 * Send a user's Stripe account details to the backend to enable the Stripe
 * integration. Resolves with the parsed JSON body on success; throws an Error
 * carrying a human-readable message otherwise.
 */
export async function connectStripe(details) {
  const csrf = getCsrfToken()
  const response = await fetch(apiUrl(STRIPE_CONNECT_PATH), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(csrf ? { 'X-CSRFToken': csrf } : {}),
    },
    body: JSON.stringify(details),
  })

  let data = null
  try {
    data = await response.json()
  } catch {
    // non-JSON response (e.g. 500 HTML page) — fall through to status handling
  }

  if (!response.ok) {
    const message =
      data?.detail || data?.error || `Request failed (${response.status})`
    throw new Error(message)
  }
  return data
}
