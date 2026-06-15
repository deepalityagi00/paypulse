import { Link } from 'react-router-dom'
import GoogleIcon from '../components/GoogleIcon.jsx'
import HowItWorks from '../components/HowItWorks.jsx'
import './home.css'

const AUDIENCES = [
  { icon: '💻', label: 'Freelancers' },
  { icon: '🏪', label: 'Small businesses' },
  { icon: '📣', label: 'Creators & influencers' },
]

const PAINS = [
  {
    icon: '📥',
    title: 'Invoices buried in your inbox',
    body: 'Receipts, invoices and "did you get my last email?" threads scattered across hundreds of messages. You can never find the one you need.',
  },
  {
    icon: '🧮',
    title: 'No idea who actually owes you',
    body: 'You think a few clients are late — but which ones, how much, and for how long? Working it out means a spreadsheet and an evening you’ll never get back.',
  },
  {
    icon: '🔁',
    title: 'Following up is awkward and endless',
    body: 'Writing the polite-but-firm reminder. Again. And next week. And the week after. Chasing money is the part of the job nobody signed up for.',
  },
  {
    icon: '🧾',
    title: 'Tax season is a scramble',
    body: 'When filing comes around you’re reconstructing a year of payments from memory, bank statements and gut feeling.',
  },
]

const FEATURES = [
  {
    icon: '📊',
    title: 'One clear dashboard',
    body: 'Outstanding, overdue and paid — at a glance, by client and category. Stop guessing where your money is.',
  },
  {
    icon: '🏷️',
    title: 'Custom categories',
    body: 'Organize invoices by vendor, client, project or type. Your business, your buckets.',
  },
  {
    icon: '✍️',
    title: 'Done-for-you follow-ups',
    body: 'We draft every reminder in your voice. You stay in control — review and approve before anything sends.',
  },
  {
    icon: '💳',
    title: 'Stripe payment links',
    body: 'Attach a payment link to any invoice. Clients pay in seconds and it reconciles itself.',
  },
  {
    icon: '📁',
    title: 'Tax-ready reports',
    body: 'One report that summarizes the year’s income and payments — built to make filing painless.',
  },
  {
    icon: '🔔',
    title: 'Automatic tracking',
    body: 'Every invoice is watched for you. The moment something is paid or overdue, you know.',
  },
]

export default function Home() {
  return (
    <>
      {/* ---------------- HERO ---------------- */}
      <section className="hero">
        <div className="container hero__inner">
          <div className="hero__copy">
            <span className="pill">
              <span className="dot" /> Invoice tracking on autopilot
            </span>
            <h1>
              Stop chasing invoices.
              <br />
              <span className="text-accent">Start getting paid.</span>
            </h1>
            <p className="hero__lead">
              PayPulse tracks every client and vendor invoice, tells you exactly
              who hasn’t paid, drafts the follow-up email for you, and records
              Stripe payments automatically. You just click send.
            </p>

            <div className="hero__actions">
              <Link to="/signin" className="btn btn--primary btn--lg">
                <span className="g-chip"><GoogleIcon size={16} /></span>Sign up with Gmail
              </Link>
              <a href="#how" className="btn btn--ghost btn--lg">
                See how it works
              </a>
            </div>

            <ul className="hero__audience">
              {AUDIENCES.map((a) => (
                <li key={a.label}>
                  <span aria-hidden="true">{a.icon}</span> {a.label}
                </li>
              ))}
            </ul>
          </div>

          <div className="hero__panel" aria-hidden="true">
            <DashboardPreview />
          </div>
        </div>
      </section>

      {/* ---------------- PROBLEM ---------------- */}
      <section className="section section--muted" id="problem">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">Sound familiar?</span>
            <h2>Running the business is the job. Chasing payments shouldn’t be.</h2>
            <p>
              When you’re a team of one, every unpaid invoice is yours to track,
              remember and politely nag about. It’s exhausting — and it’s the
              part that quietly eats your time and your cash flow.
            </p>
          </div>

          <div className="grid pains">
            {PAINS.map((p) => (
              <article className="card pain" key={p.title}>
                <span className="pain__icon" aria-hidden="true">
                  {p.icon}
                </span>
                <h3>{p.title}</h3>
                <p>{p.body}</p>
              </article>
            ))}
          </div>

          <p className="problem__turn center">
            Here’s the thing — <strong>you don’t have to do any of it.</strong>
            <br />
            Hand the whole burden to PayPulse.
          </p>
        </div>
      </section>

      {/* ---------------- HOW IT WORKS ---------------- */}
      <section className="section" id="how">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">How it works</span>
            <h2>Five steps. Then it runs itself.</h2>
            <p>Tap any step to follow the flow.</p>
          </div>

          <HowItWorks />
        </div>
      </section>

      {/* ---------------- FEATURES ---------------- */}
      <section className="section section--muted" id="features">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">Everything in one place</span>
            <h2>Less admin. More getting paid.</h2>
          </div>

          <div className="grid features">
            {FEATURES.map((f) => (
              <article className="card feature" key={f.title}>
                <span className="feature__icon" aria-hidden="true">
                  {f.icon}
                </span>
                <h3>{f.title}</h3>
                <p>{f.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- STRIPE ---------------- */}
      <section className="section stripe-band" id="stripe">
        <div className="container stripe-band__inner">
          <div className="stripe-band__copy">
            <span className="eyebrow">Built-in payments</span>
            <h2>Send a link. Get paid. It records itself.</h2>
            <p>
              Connect your Stripe account and PayPulse can attach a secure
              payment link to any invoice. Your client pays in a couple of taps,
              and the payment is matched to the right invoice and logged on the
              platform — no manual reconciling, no copy-pasting into a
              spreadsheet.
            </p>
            <ul className="ticks">
              <li>Vendor pays securely via Stripe</li>
              <li>Payment auto-matched to the invoice</li>
              <li>Status flips to “Paid” the moment it clears</li>
            </ul>
            <Link to="/signin" className="btn btn--primary btn--lg">
              Connect Gmail & Stripe
            </Link>
          </div>
          <div className="stripe-band__card" aria-hidden="true">
            <PaymentPreview />
          </div>
        </div>
      </section>

      {/* ---------------- PRICING / CTA ---------------- */}
      <section className="section" id="pricing">
        <div className="container">
          <div className="cta">
            <span className="eyebrow">One click. One report. Zero chasing.</span>
            <h2>Give the busywork to us.</h2>
            <p>
              Sign up free with Gmail, connect Stripe whenever you’re ready, and
              let PayPulse keep your invoices tracked and your follow-ups
              handled. Cancel anytime.
            </p>
            <div className="cta__actions">
              <Link to="/signin" className="btn btn--primary btn--lg">
                <span className="g-chip"><GoogleIcon size={16} /></span>Get started with Gmail
              </Link>
              <Link to="/about" className="btn btn--light btn--lg">
                Learn more about PayPulse
              </Link>
            </div>
            <p className="cta__fine">
              Free to start · No credit card required · Your inbox data stays
              private
            </p>
          </div>
        </div>
      </section>
    </>
  )
}

/* ---------- decorative inline previews (pure presentation) ---------- */

function DashboardPreview() {
  return (
    <div className="preview">
      <div className="preview__top">
        <span className="preview__title">Outstanding</span>
        <span className="preview__amount">$12,480</span>
      </div>
      <div className="preview__rows">
        {[
          { c: 'Northwind Studio', t: 'Design retainer', d: '3 days overdue', s: 'late' },
          { c: 'Acme Co.', t: 'Brand campaign', d: 'Due tomorrow', s: 'due' },
          { c: 'Lumen Media', t: 'Sponsorship', d: 'Paid via Stripe', s: 'paid' },
          { c: 'Volt Agency', t: 'Consulting', d: '11 days overdue', s: 'late' },
        ].map((r) => (
          <div className="preview__row" key={r.c}>
            <span className="preview__avatar">{r.c.charAt(0)}</span>
            <div className="preview__meta">
              <strong>{r.c}</strong>
              <small>{r.t}</small>
            </div>
            <span className={`preview__status preview__status--${r.s}`}>{r.d}</span>
          </div>
        ))}
      </div>
      <div className="preview__foot">
        <span>4 reminders drafted</span>
        <span className="preview__cta">Review &amp; send →</span>
      </div>
    </div>
  )
}

function PaymentPreview() {
  return (
    <div className="paycard">
      <div className="paycard__brand">PayPulse · Invoice #1043</div>
      <div className="paycard__amount">$1,200.00</div>
      <div className="paycard__line">
        <span>Northwind Studio</span>
        <span className="paycard__badge">Stripe</span>
      </div>
      <div className="paycard__field">Card number</div>
      <div className="paycard__input">4242 4242 4242 4242</div>
      <button className="btn btn--primary btn--block" tabIndex={-1}>
        Pay $1,200.00
      </button>
      <div className="paycard__secure">🔒 Secured by Stripe</div>
    </div>
  )
}
