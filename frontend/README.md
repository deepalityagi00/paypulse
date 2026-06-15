# PayPulse — Frontend

React + Vite marketing site & onboarding flow for PayPulse, the invoice-tracking
and payment-follow-up assistant for freelancers, small businesses and creators.

It is a standalone SPA that talks to the Django backend in [`../backend`](../backend)
over HTTP, so the two can be developed, built and deployed independently.

## Pages

| Route      | Page    | Purpose                                                             |
| ---------- | ------- | ------------------------------------------------------------------- |
| `/`        | Home    | Marketing landing — the problem, the solution, how it works, Stripe |
| `/about`   | About   | Mission, principles and who PayPulse is for                         |
| `/signin`  | Sign in | 2-step onboarding: Gmail OAuth → optional Stripe connect            |

## Stack

- **React 19** + **React Router 7**
- **Vite 6** build tooling
- Plain CSS with a small design-token system (`src/styles/index.css`) — no UI
  framework, so the bundle stays lean.

## Getting started

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

Run the Django backend alongside it on `:8000`:

```bash
cd ../backend
../.venv/bin/python manage.py runserver
```

The Vite dev server **proxies** `/gmail`, `/stripe`, `/api` and `/health` to
`http://localhost:8000` (see `vite.config.js`), so the browser sees a single
origin — no CORS configuration needed in development.

## Backend integration

All backend wiring lives in `src/config.js` and `src/api/client.js`:

- **Gmail sign-in** → clicking _Continue with Gmail_ opens a Google-styled
  sign-in popup (`GoogleAuthModal`), then `startGmailAuth(email)` navigates the
  browser to `GET /gmail/auth/` (`GmailAuthInitView`, public). The backend
  redirects to Google's consent screen; after consent, the callback
  (`GmailCallbackView`) creates-or-logs-in the user from their Google email,
  stores the encrypted tokens, and redirects back here to
  `/signin?gmail=connected&email=…` (or `?gmail=error&reason=…`). The SPA reads
  those params to show a banner and advance to the Stripe step.
- **Stripe connect** → `connectStripe(details)` POSTs the account details to
  `POST /stripe/connect/` with the Django CSRF token from the `csrftoken`
  cookie. Works once the user is signed in (the OAuth callback set the session).

> **Note:** `POST /stripe/connect/` is the endpoint this UI expects the backend
> to expose for storing a user's Stripe account credentials. If your backend
> uses a different path, override it via `VITE_STRIPE_CONNECT_PATH`.

### Environment variables

Copy `.env.example` to `.env` and adjust as needed:

| Variable                   | Default            | Notes                                             |
| -------------------------- | ------------------ | ------------------------------------------------- |
| `VITE_API_BASE_URL`        | _(empty)_          | Empty = same origin (dev proxy). Set for prod.    |
| `VITE_GMAIL_AUTH_PATH`     | `/gmail/auth/`     | Backend Gmail OAuth entrypoint.                   |
| `VITE_STRIPE_CONNECT_PATH` | `/stripe/connect/` | Backend endpoint that stores Stripe credentials.  |

## Production build

```bash
npm run build        # outputs static assets to dist/
npm run preview      # preview the production build locally
```

The `dist/` folder can be served by any static host, or by Django/WhiteNoise
(already a backend dependency) if you prefer a single deployment.
