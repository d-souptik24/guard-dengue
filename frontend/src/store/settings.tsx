/**
 * GuardDengue — Global App Settings Store
 *
 * Manages language (en/bn), inspector mode, fontSize (sm/md/lg), and contrast (normal/high).
 * Uses React Context + useReducer with synchronous localStorage initialization and DOM sync.
 *
 * Conforms to WCAG 2.1 AA and GIGW 3.0 accessibility standards.
 */
import { createContext, useContext, useReducer, useEffect, type ReactNode } from 'react'
import type { AppSettings, AppLanguage, FontSize, ContrastMode } from '@/types'

// ─── LocalStorage Contract ───────────────────────────────────────────────────

const STORAGE_KEY = 'guarddengue_settings'
const STORAGE_VERSION = 1

interface PersistedSettings {
  version: number
  language: AppLanguage
  inspectorMode: boolean
  fontSize: FontSize
  contrast: ContrastMode
}

// ─── Initial State ────────────────────────────────────────────────────────────

const INITIAL_SETTINGS: AppSettings = {
  language: 'en',
  inspectorMode: false,
  fontSize: 'md',
  contrast: 'normal',
}

// ─── DOM Synchronization ─────────────────────────────────────────────────────

const FONT_SIZE_MAP: Record<FontSize, string> = {
  sm: '14px',
  md: '16px',
  lg: '18px',
}

export function applySettingsToDOM(settings: AppSettings): void {
  if (typeof document === 'undefined') return

  // Sync language for CSS :lang(bn) selector and screen readers
  document.documentElement.lang = settings.language

  // Sync contrast mode for [data-contrast="high"] token overrides
  document.documentElement.setAttribute('data-contrast', settings.contrast)

  // Sync root font size to scale rem units across all typography
  document.documentElement.style.fontSize = FONT_SIZE_MAP[settings.fontSize] || '16px'
}

function loadInitialSettings(): AppSettings {
  if (typeof window === 'undefined') return INITIAL_SETTINGS
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      applySettingsToDOM(INITIAL_SETTINGS)
      return INITIAL_SETTINGS
    }
    const parsed: PersistedSettings = JSON.parse(raw)
    if (parsed?.version !== STORAGE_VERSION) {
      applySettingsToDOM(INITIAL_SETTINGS)
      return INITIAL_SETTINGS
    }
    const loaded: AppSettings = {
      language: parsed.language === 'bn' ? 'bn' : 'en',
      inspectorMode: Boolean(parsed.inspectorMode),
      fontSize: ['sm', 'md', 'lg'].includes(parsed.fontSize) ? parsed.fontSize : 'md',
      contrast: parsed.contrast === 'high' ? 'high' : 'normal',
    }
    applySettingsToDOM(loaded)
    return loaded
  } catch {
    applySettingsToDOM(INITIAL_SETTINGS)
    return INITIAL_SETTINGS
  }
}

// ─── Actions ──────────────────────────────────────────────────────────────────

type Action =
  | { type: 'SET_LANGUAGE'; payload: AppLanguage }
  | { type: 'SET_FONT_SIZE'; payload: FontSize }
  | { type: 'SET_CONTRAST'; payload: ContrastMode }
  | { type: 'TOGGLE_INSPECTOR' }

function settingsReducer(state: AppSettings, action: Action): AppSettings {
  switch (action.type) {
    case 'SET_LANGUAGE':
      return { ...state, language: action.payload }
    case 'SET_FONT_SIZE':
      return { ...state, fontSize: action.payload }
    case 'SET_CONTRAST':
      return { ...state, contrast: action.payload }
    case 'TOGGLE_INSPECTOR':
      return { ...state, inspectorMode: !state.inspectorMode }
    default:
      return state
  }
}

// ─── Context ──────────────────────────────────────────────────────────────────

interface SettingsContextValue {
  settings: AppSettings
  setLanguage: (lang: AppLanguage) => void
  setFontSize: (size: FontSize) => void
  setContrast: (mode: ContrastMode) => void
  toggleInspector: () => void
}

const SettingsContext = createContext<SettingsContextValue | null>(null)

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, dispatch] = useReducer(settingsReducer, undefined, loadInitialSettings)

  // Persist and apply settings whenever state updates
  useEffect(() => {
    applySettingsToDOM(settings)
    try {
      const persisted: PersistedSettings = {
        version: STORAGE_VERSION,
        language: settings.language,
        inspectorMode: settings.inspectorMode,
        fontSize: settings.fontSize,
        contrast: settings.contrast,
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(persisted))
    } catch {
      // Ignore localStorage write failures (e.g. private browsing quota)
    }
  }, [settings])

  return (
    <SettingsContext.Provider
      value={{
        settings,
        setLanguage: (lang) => dispatch({ type: 'SET_LANGUAGE', payload: lang }),
        setFontSize: (size) => dispatch({ type: 'SET_FONT_SIZE', payload: size }),
        setContrast: (mode) => dispatch({ type: 'SET_CONTRAST', payload: mode }),
        toggleInspector: () => dispatch({ type: 'TOGGLE_INSPECTOR' }),
      }}
    >
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const ctx = useContext(SettingsContext)
  if (!ctx) throw new Error('useSettings must be used within SettingsProvider')
  return ctx
}
