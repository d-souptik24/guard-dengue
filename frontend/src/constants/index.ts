/**
 * GuardDengue — Application Constants
 *
 * Centralizes all static configuration: API endpoints, clinical quick prompts,
 * knowledge topic labels, emergency contacts, and source authority display names.
 */
import type { KnowledgeTopic, AppLanguage } from '@/types'

// ─── API Endpoints ────────────────────────────────────────────────────────────
export const API_BASE = '/api'
export const ENDPOINTS = {
  chat:     `${API_BASE}/chat`,
  stream:   `${API_BASE}/chat/stream`,
  health:   `${API_BASE}/health`,
  session:  `${API_BASE}/session`,
} as const

// ─── Bengali Emergency Contacts (West Bengal Health Dept) ────────────────────
export const EMERGENCY_CONTACTS = {
  stateHealth:  '1800-313444-222',   // Swasthya Bhawan toll-free
  nationalNBVD: '011-23737831',      // NCVBDC Delhi
  ambulance:    '108',
} as const

// ─── Knowledge Base Topic Display Names ──────────────────────────────────────
export const TOPIC_LABELS: Record<KnowledgeTopic, Record<AppLanguage, string>> = {
  'Dengue basics':       { en: 'Dengue Basics',        bn: 'ডেঙ্গু পরিচিতি' },
  'Transmission':        { en: 'Transmission',          bn: 'সংক্রমণ পথ' },
  'Symptoms':            { en: 'Symptoms',              bn: 'লক্ষণ ও উপসর্গ' },
  'Prevention':          { en: 'Prevention',            bn: 'প্রতিরোধ' },
  'Hydration':           { en: 'Hydration',             bn: 'জলপান ও তরল' },
  'Warning signs':       { en: 'Warning Signs',         bn: 'সতর্কতা চিহ্ন' },
  'Diagnosis':           { en: 'Diagnosis',             bn: 'রোগ নির্ণয়' },
  'Myths':               { en: 'Myths & Facts',         bn: 'মিথ ও তথ্য' },
  'Children':            { en: 'Children',              bn: 'শিশু রোগী' },
  'Pregnancy':           { en: 'Pregnancy',             bn: 'গর্ভাবস্থা' },
  'Medication safety':   { en: 'Medication Safety',     bn: 'ওষুধ সুরক্ষা' },
  'Outbreak awareness':  { en: 'Outbreak Awareness',    bn: 'প্রাদুর্ভাব সচেতনতা' },
  'Emergency guidance':  { en: 'Emergency Guidance',    bn: 'জরুরি নির্দেশনা' },
}

// ─── Quick-Prompt Suggestions (shown below input on load) ────────────────────
export const QUICK_PROMPTS: Record<AppLanguage, string[]> = {
  en: [
    'What are the warning signs when fever drops?',
    'Can I take ibuprofen or aspirin for dengue fever?',
    'What should I do if I have severe stomach pain and vomiting?',
    'What is the platelet transfusion threshold for dengue?',
    'How does dengue spread from mosquitoes?',
    'I am pregnant and may have dengue — what should I do?',
  ],
  bn: [
    'জ্বর কমলে কোন লক্ষণগুলো দেখতে হবে?',
    'ডেঙ্গুতে আইবুপ্রোফেন বা অ্যাসপিরিন খাওয়া যাবে?',
    'পেটে তীব্র ব্যথা ও বমি হচ্ছে — এখন কী করা উচিত?',
    'ডেঙ্গুতে প্লেটলেট ট্রান্সফিউশন কখন দরকার?',
    'মশা থেকে ডেঙ্গু কীভাবে ছড়ায়?',
    'আমি গর্ভবতী এবং ডেঙ্গু সন্দেহ হচ্ছে — এখন কী করব?',
  ],
}

// ─── Source Authority Display Map ─────────────────────────────────────────────
export const SOURCE_DISPLAY: Record<string, string> = {
  'WHO Dengue Guidelines':                      'WHO',
  'WHO Clinical Management Guidelines':         'WHO Clinical',
  'WHO Clinical Guidelines for Dengue Case Management': 'WHO Case Mgmt',
  'WHO Clinical Guidelines & US CDC':           'WHO & CDC',
  'NCVBDC National Operational Guidelines':     'NCVBDC',
  'ICMR Guidelines for Laboratory Diagnosis of Dengue': 'ICMR',
  'Indian Academy of Pediatrics (IAP) Guidelines': 'IAP',
  'FOGSI & WHO Guidelines on Dengue in Pregnancy': 'FOGSI / WHO',
  'Ministry of Health and Family Welfare (MoHFW)': 'MoHFW',
  'CDC Dengue Prevention Protocols':            'CDC',
  'Systematic Review on Phytotherapies in Dengue (BMC Infectious Diseases)': 'BMC Infect Dis',
}

// ─── Route → UI mapping ───────────────────────────────────────────────────────
export const ROUTE_CONFIG = {
  urgent:     { label: 'Emergency',          color: 'zone-emergency',   icon: 'AlertOctagon'  },
  medication: { label: 'Medication Safety',  color: 'zone-medication',  icon: 'ShieldAlert'   },
  education:  { label: 'Health Information', color: 'zone-verified',    icon: 'BookOpen'      },
  uncertain:  { label: 'Unable to Answer',   color: 'zone-uncertain',   icon: 'HelpCircle'    },
} as const
