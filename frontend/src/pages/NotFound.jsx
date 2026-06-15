import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <section className="section">
      <div className="container center">
        <span className="eyebrow">404</span>
        <h1>This page took an early payment and left.</h1>
        <p style={{ color: 'var(--text-soft)', maxWidth: 460, margin: '0 auto 24px' }}>
          The page you’re looking for doesn’t exist. Let’s get you back on track.
        </p>
        <Link to="/" className="btn btn--primary btn--lg">
          Back to home
        </Link>
      </div>
    </section>
  )
}
