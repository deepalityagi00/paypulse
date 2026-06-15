import { useEffect, useRef, useState } from 'react'
import './googleauthmodal.css'

// A Google-styled "Sign in" popup. It deliberately mirrors Google's real
// account screen (wordmark, email step) but never asks for a password —
// credentials are entered on Google's own domain after we hand off to the
// backend OAuth endpoint. `onContinue(email)` fires on Next.
export default function GoogleAuthModal({ open, onClose, onContinue }) {
  const [email, setEmail] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    const focus = setTimeout(() => inputRef.current?.focus(), 60)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
      clearTimeout(focus)
    }
  }, [open, onClose])

  if (!open) return null

  const submit = (e) => {
    e.preventDefault()
    onContinue(email.trim())
  }

  return (
    <div className="gauth__overlay" onMouseDown={onClose}>
      <div
        className="gauth"
        role="dialog"
        aria-modal="true"
        aria-labelledby="gauth-title"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <button className="gauth__close" aria-label="Close" onClick={onClose}>
          ✕
        </button>

        <div className="gauth__head">
          <GoogleWordmark />
          <h1 id="gauth-title" className="gauth__title">
            Sign in
          </h1>
          <p className="gauth__sub">
            to continue to <span>PayPulse</span>
          </p>
        </div>

        <form className="gauth__body" onSubmit={submit}>
          <div className="gauth__field">
            <input
              ref={inputRef}
              id="gauth-email"
              type="email"
              className="gauth__input"
              placeholder=" "
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
            />
            <label htmlFor="gauth-email" className="gauth__floating">
              Email or phone
            </label>
          </div>

          <a
            className="gauth__link"
            href="#forgot"
            onClick={(e) => e.preventDefault()}
          >
            Forgot email?
          </a>

          <p className="gauth__guest">
            To continue, Google will share your name, email address and profile
            picture with PayPulse. No password is entered here.
          </p>

          <div className="gauth__actions">
            <a
              className="gauth__create"
              href="#create"
              onClick={(e) => e.preventDefault()}
            >
              Create account
            </a>
            <button type="submit" className="gauth__next">
              Next
            </button>
          </div>
        </form>

        <div className="gauth__footer">
          <span>English (United States)</span>
          <span className="gauth__footer-links">
            <a href="#help" onClick={(e) => e.preventDefault()}>
              Help
            </a>
            <a href="#privacy" onClick={(e) => e.preventDefault()}>
              Privacy
            </a>
            <a href="#terms" onClick={(e) => e.preventDefault()}>
              Terms
            </a>
          </span>
        </div>
      </div>
    </div>
  )
}

// Google's four-colour wordmark.
function GoogleWordmark() {
  const colors = ['#4285F4', '#EA4335', '#FBBC05', '#4285F4', '#34A853', '#EA4335']
  return (
    <div className="gauth__logo" aria-label="Google">
      {'Google'.split('').map((ch, i) => (
        <span key={i} style={{ color: colors[i] }}>
          {ch}
        </span>
      ))}
    </div>
  )
}
