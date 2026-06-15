import { Link } from 'react-router-dom'
import './about.css'

const VALUES = [
  {
    icon: '🎯',
    title: 'Built for one-person teams',
    body: 'PayPulse is designed for the freelancer, the small shop and the creator who is also the accountant, the chaser and the boss. We optimize for your time.',
  },
  {
    icon: '🔐',
    title: 'Your data stays yours',
    body: 'We connect to Gmail with read access to find invoices — nothing more. Tokens are encrypted, and you can disconnect any time.',
  },
  {
    icon: '🙌',
    title: 'You stay in control',
    body: 'We draft, you decide. No email is ever sent and no payment is ever requested without your review and approval.',
  },
  {
    icon: '⚡',
    title: 'Automation that earns its keep',
    body: 'Categorizing, tracking, reminding, reconciling — the repetitive work runs itself so you can get back to the work you’re actually paid for.',
  },
]

const STATS = [
  { value: '1 click', label: 'to send a drafted follow-up' },
  { value: '1 report', label: 'that makes filing taxes simple' },
  { value: '0 spreadsheets', label: 'to maintain by hand' },
]

export default function About() {
  return (
    <>
      <section className="about-hero">
        <div className="container">
          <span className="pill">
            <span className="dot" /> About PayPulse
          </span>
          <h1>
            We handle the chasing,
            <br />
            so you can do the work.
          </h1>
          <p className="about-hero__lead">
            PayPulse started with a simple frustration: getting paid as an
            independent shouldn’t take more effort than the work itself. Yet
            every freelancer, small business and creator we knew was losing
            evenings to tracking invoices, remembering who owed what, and writing
            the same awkward reminder over and over.
          </p>
          <p className="about-hero__lead">
            So we built the assistant we wished we had — one that reads the
            invoices already in your inbox, keeps a running tally of what you’re
            owed, drafts the follow-ups, and records payments automatically the
            moment they clear through Stripe.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="about-stats">
            {STATS.map((s) => (
              <div className="about-stat" key={s.label}>
                <span className="about-stat__value">{s.value}</span>
                <span className="about-stat__label">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section section--muted">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">What we believe</span>
            <h2>A few principles we won’t compromise on</h2>
          </div>
          <div className="grid about-values">
            {VALUES.map((v) => (
              <article className="card about-value" key={v.title}>
                <span className="about-value__icon" aria-hidden="true">
                  {v.icon}
                </span>
                <h3>{v.title}</h3>
                <p>{v.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container about-mission">
          <div>
            <span className="eyebrow">Who it’s for</span>
            <h2>If you invoice people, PayPulse is for you.</h2>
            <p>
              Whether you’re a designer juggling client retainers, a small studio
              billing vendors, or a creator managing brand sponsorships — the
              admin is the same, and it’s relentless. PayPulse takes the invoice
              tracking, the follow-ups and the payment recording off your plate
              entirely. You get clarity on what you’re owed, and a single report
              that turns tax season from a scramble into a download.
            </p>
            <Link to="/signin" className="btn btn--primary btn--lg">
              Get started with Gmail
            </Link>
          </div>
          <ul className="about-audience-list">
            <li>
              <strong>Freelancers</strong>
              <span>Designers, developers, writers, consultants — anyone billing clients.</span>
            </li>
            <li>
              <strong>Small businesses</strong>
              <span>Studios and shops tracking vendor and customer invoices in one place.</span>
            </li>
            <li>
              <strong>Creators &amp; influencers</strong>
              <span>Managing sponsorship and brand-deal payments without the chaos.</span>
            </li>
          </ul>
        </div>
      </section>
    </>
  )
}
