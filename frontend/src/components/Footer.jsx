import { Link } from 'react-router-dom'
import Logo from './Logo.jsx'
import './footer.css'

export default function Footer() {
  const year = new Date().getFullYear()
  return (
    <footer className="footer">
      <div className="container footer__inner">
        <div className="footer__brand">
          <Logo light />
          <p>
            Invoice tracking and payment follow-ups on autopilot — built for
            freelancers, small businesses and creators.
          </p>
        </div>

        <div className="footer__cols">
          <div className="footer__col">
            <h4>Product</h4>
            <a href="/#how">How it works</a>
            <a href="/#features">Features</a>
            <a href="/#pricing">Pricing</a>
            <Link to="/signin">Get started</Link>
          </div>
          <div className="footer__col">
            <h4>Company</h4>
            <Link to="/about">About</Link>
            <a href="/#faq">FAQ</a>
            <a href="mailto:hello@paypulse.app">Contact</a>
          </div>
          <div className="footer__col">
            <h4>Legal</h4>
            <a href="#privacy">Privacy</a>
            <a href="#terms">Terms</a>
            <a href="#security">Security</a>
          </div>
        </div>
      </div>

      <div className="container footer__bar">
        <span>© {year} PayPulse. All rights reserved.</span>
        <span className="footer__made">Made for people who hate chasing invoices.</span>
      </div>
    </footer>
  )
}
