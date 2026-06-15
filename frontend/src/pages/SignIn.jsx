import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import GoogleIcon from '../components/GoogleIcon.jsx'
import GoogleAuthModal from '../components/GoogleAuthModal.jsx'
import { startGmailAuth, connectStripe } from '../api/client.js'
import './signin.css'

// Human-readable copy for the error reasons the backend can hand back.
const ERROR_COPY = {
  invalid_state: 'Your sign-in session expired. Please try again.',
  missing_code: 'Google didn’t return an authorization code. Please try again.',
  exchange_failed: 'We couldn’t complete sign-in with Google. Please try again.',
  no_email: 'We couldn’t read your email from Google. Please try again.',
  access_denied: 'Sign-in was cancelled.',
}

export default function SignIn() {
  // Two-step onboarding: 1) sign in with Gmail, 2) optionally connect Stripe.
  const [step, setStep] = useState(1)
  const [searchParams, setSearchParams] = useSearchParams()
  const [connectedEmail, setConnectedEmail] = useState('')
  const [authError, setAuthError] = useState('')

  // React to the OAuth redirect (…/signin?gmail=connected|error).
  useEffect(() => {
    const gmail = searchParams.get('gmail')
    if (!gmail) return
    if (gmail === 'connected') {
      setConnectedEmail(searchParams.get('email') || '')
      setStep(2) // Gmail done — move on to the optional Stripe step.
    } else if (gmail === 'error') {
      const reason = searchParams.get('reason')
      setAuthError(ERROR_COPY[reason] || 'Sign-in failed. Please try again.')
    }
    // Clear the query so a refresh doesn’t replay the banner.
    setSearchParams({}, { replace: true })
  }, [searchParams, setSearchParams])

  return (
    <section className="auth">
      <div className="container auth__grid">
        {/* Left: value reminder */}
        <aside className="auth__aside">
          <Link to="/" className="auth__logo-link">
            ← Back to home
          </Link>
          <h1>Let’s get you set up.</h1>
          <p className="auth__sub">
            Two quick steps and PayPulse starts tracking your invoices and
            drafting your follow-ups.
          </p>

          <ol className="auth__steps">
            <li className={step >= 1 ? 'is-active' : ''}>
              <span className="auth__step-n">1</span>
              <div>
                <strong>Sign in with Gmail</strong>
                <small>So we can find the invoices in your inbox.</small>
              </div>
            </li>
            <li className={step >= 2 ? 'is-active' : ''}>
              <span className="auth__step-n">2</span>
              <div>
                <strong>Connect Stripe</strong>
                <small>Optional — enables payment links &amp; auto-recording.</small>
              </div>
            </li>
          </ol>

          <ul className="auth__assurances">
            <li>🔒 Read-only Gmail access — we never send without your approval</li>
            <li>🛡️ Tokens are encrypted at rest</li>
            <li>↩️ Disconnect anytime</li>
          </ul>
        </aside>

        {/* Right: the active step */}
        <div className="auth__panel">
          {authError && (
            <div className="auth__banner auth__banner--error" role="alert">
              {authError}
            </div>
          )}
          {connectedEmail && (
            <div className="auth__banner auth__banner--success" role="status">
              ✓ Signed in as <strong>{connectedEmail}</strong>
            </div>
          )}
          {step === 1 ? (
            <GmailStep onSkipToStripe={() => setStep(2)} />
          ) : (
            <StripeStep onBack={() => setStep(1)} />
          )}
        </div>
      </div>
    </section>
  )
}

/* ------------------------- Step 1: Gmail ------------------------- */
function GmailStep({ onSkipToStripe }) {
  const [authOpen, setAuthOpen] = useState(false)

  return (
    <div className="auth__card">
      <span className="pill">
        <span className="dot" /> Step 1 of 2
      </span>
      <h2>Sign up with Gmail</h2>
      <p className="auth__card-lead">
        PayPulse uses your Google account to sign you in and to find invoice and
        payment emails. We ask only for the access we need.
      </p>

      <button className="btn auth__google" onClick={() => setAuthOpen(true)}>
        <span className="g-chip">
          <GoogleIcon size={18} />
        </span>
        Continue with Gmail
      </button>

      <GoogleAuthModal
        open={authOpen}
        onClose={() => setAuthOpen(false)}
        onContinue={(email) => startGmailAuth(email)}
      />

      <p className="auth__legal">
        By continuing you agree to PayPulse’s{' '}
        <a href="#terms">Terms</a> and <a href="#privacy">Privacy Policy</a>.
      </p>

      <div className="auth__divider"><span>then</span></div>

      <button className="btn btn--ghost btn--block" onClick={onSkipToStripe}>
        Set up Stripe payments →
      </button>
      <p className="auth__hint center">
        You can connect Stripe now or later from your dashboard.
      </p>
    </div>
  )
}

/* ------------------------- Step 2: Stripe ------------------------- */
const EMPTY_STRIPE = {
  account_name: '',
  account_id: '',
  publishable_key: '',
  secret_key: '',
}

function StripeStep({ onBack }) {
  const [form, setForm] = useState(EMPTY_STRIPE)
  const [errors, setErrors] = useState({})
  const [status, setStatus] = useState('idle') // idle | saving | success | error
  const [serverError, setServerError] = useState('')

  const update = (key) => (e) => {
    setForm((f) => ({ ...f, [key]: e.target.value }))
    setErrors((prev) => ({ ...prev, [key]: undefined }))
  }

  const validate = () => {
    const next = {}
    if (!form.account_name.trim())
      next.account_name = 'Give this account a name you’ll recognize.'
    if (!/^acct_[A-Za-z0-9]+$/.test(form.account_id.trim()))
      next.account_id = 'Stripe account IDs look like “acct_1A2b3C…”.'
    if (!/^pk_(test|live)_[A-Za-z0-9]+$/.test(form.publishable_key.trim()))
      next.publishable_key = 'Publishable keys start with pk_test_ or pk_live_.'
    if (!/^(sk|rk)_(test|live)_[A-Za-z0-9]+$/.test(form.secret_key.trim()))
      next.secret_key = 'Use a secret or restricted key (sk_… or rk_…).'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    setServerError('')
    if (!validate()) return
    setStatus('saving')
    try {
      await connectStripe({
        account_name: form.account_name.trim(),
        account_id: form.account_id.trim(),
        publishable_key: form.publishable_key.trim(),
        secret_key: form.secret_key.trim(),
      })
      setStatus('success')
    } catch (err) {
      setStatus('error')
      setServerError(err.message || 'Could not save your Stripe details.')
    }
  }

  if (status === 'success') {
    return (
      <div className="auth__card auth__card--center">
        <div className="auth__success">✓</div>
        <h2>Stripe connected</h2>
        <p className="auth__card-lead">
          You’re all set. PayPulse can now attach payment links to your invoices
          and record payments automatically as they clear.
        </p>
        <a className="btn btn--primary btn--block btn--lg" href="/">
          Go to dashboard
        </a>
      </div>
    )
  }

  return (
    <form className="auth__card" onSubmit={onSubmit} noValidate>
      <span className="pill">
        <span className="dot" /> Step 2 of 2 · Optional
      </span>
      <h2>Connect your Stripe account</h2>
      <p className="auth__card-lead">
        Add your Stripe details to enable payment links and automatic recording.
        You can find these in your{' '}
        <a href="https://dashboard.stripe.com/apikeys" target="_blank" rel="noreferrer">
          Stripe Dashboard → API keys
        </a>
        .
      </p>

      <Field
        label="Account name"
        placeholder="e.g. My Studio LLC"
        value={form.account_name}
        onChange={update('account_name')}
        error={errors.account_name}
        autoComplete="organization"
      />
      <Field
        label="Stripe account ID"
        placeholder="acct_1A2b3C4d5E6f"
        value={form.account_id}
        onChange={update('account_id')}
        error={errors.account_id}
        mono
      />
      <Field
        label="Publishable key"
        placeholder="pk_live_…"
        value={form.publishable_key}
        onChange={update('publishable_key')}
        error={errors.publishable_key}
        mono
      />
      <Field
        label="Secret key"
        placeholder="sk_live_… or rk_live_…"
        value={form.secret_key}
        onChange={update('secret_key')}
        error={errors.secret_key}
        type="password"
        mono
        hint="Stored encrypted. We recommend a restricted key (rk_…) scoped to payments."
      />

      {serverError && <div className="auth__form-error">{serverError}</div>}

      <button
        type="submit"
        className="btn btn--primary btn--block btn--lg"
        disabled={status === 'saving'}
      >
        {status === 'saving' ? 'Saving…' : 'Enable Stripe integration'}
      </button>

      <button type="button" className="auth__back" onClick={onBack}>
        ← Back
      </button>
      <p className="auth__hint center">
        Not ready? <a href="/">Skip for now</a> — you can add this later.
      </p>
    </form>
  )
}

function Field({ label, error, hint, mono, ...props }) {
  return (
    <label className="field">
      <span className="field__label">{label}</span>
      <input
        className={`field__input ${mono ? 'field__input--mono' : ''} ${
          error ? 'field__input--error' : ''
        }`}
        {...props}
      />
      {error ? (
        <span className="field__error">{error}</span>
      ) : hint ? (
        <span className="field__hint">{hint}</span>
      ) : null}
    </label>
  )
}
