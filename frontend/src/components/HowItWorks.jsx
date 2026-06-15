import { useEffect, useRef, useState } from 'react'
import './howitworks.css'

// Short, 1–2 word labels — the detail lives in the caption under the chart.
const NODES = [
  { icon: '📥', label: 'Connect Gmail', caption: 'Sign in once — we read your invoice emails.' },
  { icon: '🏷️', label: 'Auto-sort', caption: 'Every invoice grouped by client & category.' },
  { icon: '📊', label: 'Track dues', caption: 'See who owes you, and how overdue they are.' },
  { icon: '✍️', label: 'Draft reminder', caption: 'We write the follow-up — you just review.' },
  { icon: '✅', label: 'Get paid', caption: 'Paid via Stripe, recorded automatically.' },
]

export default function HowItWorks() {
  const [active, setActive] = useState(0)
  const [autoplay, setAutoplay] = useState(true)
  const timer = useRef(null)

  // Gentle auto-advance so the flow animates on its own — until the user clicks.
  useEffect(() => {
    if (!autoplay) return
    timer.current = setInterval(() => {
      setActive((i) => (i + 1) % NODES.length)
    }, 2200)
    return () => clearInterval(timer.current)
  }, [autoplay])

  const select = (i) => {
    setAutoplay(false)
    clearInterval(timer.current)
    setActive(i)
  }

  return (
    <div className="flow" role="group" aria-label="How PayPulse works, in five steps">
      <div className="flow__track">
        {NODES.map((node, i) => {
          const done = i <= active
          const current = i === active
          return (
            <div className="flow__item" key={node.label}>
              <button
                type="button"
                className={`flow__node ${done ? 'is-done' : ''} ${
                  current ? 'is-current' : ''
                }`}
                onClick={() => select(i)}
                aria-pressed={current}
              >
                <span className="flow__num">{i + 1}</span>
                <span className="flow__icon" aria-hidden="true">
                  {node.icon}
                </span>
                <span className="flow__label">{node.label}</span>
              </button>

              {i < NODES.length - 1 && (
                <span
                  className={`flow__link ${i < active ? 'is-filled' : ''}`}
                  style={{ '--i': i }}
                  aria-hidden="true"
                >
                  <span className="flow__link-fill" />
                  <span className="flow__arrow" />
                </span>
              )}
            </div>
          )
        })}
      </div>

      <p className="flow__caption" aria-live="polite">
        <span className="flow__caption-step">Step {active + 1}</span>
        {NODES[active].caption}
      </p>
    </div>
  )
}
