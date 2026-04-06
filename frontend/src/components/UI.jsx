/**
 * AI FOR EDUCATION – Reusable Loading Shimmer Component
 */
export function LoadingShimmer({ lines = 3, className = '' }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 rounded shimmer"
          style={{ width: `${85 - i * 15}%` }}
        />
      ))}
    </div>
  )
}

/**
 * Loading Spinner
 */
export function LoadingSpinner({ size = 'md', text = 'Generating...' }) {
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <div className={`${sizeClasses[size]} border-2 border-gray-700 border-t-white rounded-full animate-spin`} />
      {text && <p className="text-sm text-gray-400 animate-pulse">{text}</p>}
    </div>
  )
}

/**
 * Card Component
 */
export function Card({ children, className = '', hover = true }) {
  return (
    <div
      className={`
        bg-gray-900 border border-gray-800 rounded-xl p-6
        ${hover ? 'card-hover' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  )
}

/**
 * Page Header
 */
export function PageHeader({ title, subtitle, icon: Icon }) {
  return (
    <div className="mb-8 animate-slide-up">
      <div className="flex items-center gap-3 mb-2">
        {Icon && (
          <div className="w-10 h-10 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center">
            <Icon size={20} strokeWidth={1.5} />
          </div>
        )}
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight">{title}</h1>
      </div>
      {subtitle && (
        <p className="text-gray-400 text-sm lg:text-base ml-[52px]">{subtitle}</p>
      )}
    </div>
  )
}

/**
 * Input Field
 */
export function Input({ label, ...props }) {
  return (
    <div className="space-y-2">
      {label && <label className="text-sm font-medium text-gray-300">{label}</label>}
      <input
        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 text-sm transition-all duration-200 focus:border-white focus:ring-1 focus:ring-white/20"
        {...props}
      />
    </div>
  )
}

/**
 * Select Field
 */
export function Select({ label, options, ...props }) {
  return (
    <div className="space-y-2">
      {label && <label className="text-sm font-medium text-gray-300">{label}</label>}
      <select
        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white text-sm transition-all duration-200 focus:border-white appearance-none cursor-pointer"
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  )
}

/**
 * Button
 */
export function Button({ children, variant = 'primary', loading = false, className = '', ...props }) {
  const variants = {
    primary:
      'bg-white text-black hover:bg-gray-200 active:bg-gray-300',
    secondary:
      'bg-gray-800 text-white border border-gray-700 hover:bg-gray-700 hover:border-gray-600',
    ghost:
      'bg-transparent text-gray-400 hover:text-white hover:bg-gray-800',
  }

  return (
    <button
      className={`
        px-6 py-3 rounded-lg text-sm font-medium transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        flex items-center justify-center gap-2
        ${variants[variant]}
        ${className}
      `}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
}

/**
 * Audio Player (minimal black theme)
 */
export function AudioPlayer({ src, className = '', onEnded }) {
  if (!src) return null

  return (
    <div className={`bg-gray-900 border border-gray-800 rounded-xl p-4 ${className}`}>
      <div className="flex items-center gap-3 mb-3">
        <div className="flex gap-[2px] items-end h-6">
          {[3, 5, 8, 4, 7, 3, 6, 4, 8, 5, 3, 7, 4, 6, 3].map((h, i) => (
            <div
              key={i}
              className="w-[3px] bg-white/40 rounded-full animate-pulse"
              style={{
                height: `${h * 2.5}px`,
                animationDelay: `${i * 0.1}s`,
                animationDuration: '1.5s',
              }}
            />
          ))}
        </div>
        <span className="text-xs text-gray-400 uppercase tracking-wider">Audio Player</span>
      </div>
      <audio
        controls
        src={src}
        onEnded={onEnded}
        className="w-full h-10 rounded-lg"
        style={{ filter: 'invert(1) hue-rotate(180deg)', opacity: 0.8 }}
      />
    </div>
  )
}
