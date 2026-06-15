// PayPulse wordmark + pulse mark. `light` renders white text for dark surfaces.
export default function Logo({ light = false }) {
  return (
    <span className={`logo ${light ? 'logo--light' : ''}`}>
      <svg
        className="logo__mark"
        viewBox="0 0 32 32"
        width="30"
        height="30"
        aria-hidden="true"
      >
        <rect width="32" height="32" rx="8" fill="var(--indigo-600)" />
        <path
          d="M5 17h4l2.5-7 4 13 3-9 2 3h6"
          fill="none"
          stroke="var(--emerald-400)"
          strokeWidth="2.4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span className="logo__text">
        Pay<span className="logo__accent">Pulse</span>
      </span>
    </span>
  )
}
