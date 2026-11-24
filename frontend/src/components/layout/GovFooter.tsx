/**
 * GovFooter — wb.gov.in Pattern Official Civic Footer
 *
 * Implements:
 * - Centered navigation links in semantic <nav>
 * - Statutory Medical Non-Diagnostic Disclaimer in English & Bengali
 * - Academic Research attribution (A.K.C.S.I.T., University of Calcutta)
 */
import { Link } from 'react-router-dom'
import { useSettings } from '@/store/settings'

export interface GovFooterProps {
  className?: string
}

export default function GovFooter({ className = '' }: GovFooterProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <footer
      role="contentinfo"
      className={`w-full bg-wb-surface border-t border-wb-border text-wb-text-muted text-xs py-6 px-4 sm:px-6 ${className}`}
    >
      <div className="w-full max-w-7xl mx-auto flex flex-col items-center text-center space-y-4">
        {/* Navigation Links */}
        <nav aria-label={isBn ? 'ফুটার নেভিগেশন' : 'Footer navigation'}>
          <ul role="list" className="flex flex-wrap items-center justify-center gap-x-3 gap-y-2 text-wb-text-main font-medium">
            <li>
              <Link to="/" className="hover:text-wb-amber-700 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-wb-amber-700 p-1">
                {isBn ? 'সহায়তা ডেস্ক' : 'Sahayata Desk'}
              </Link>
            </li>
            <li aria-hidden="true" className="text-wb-border">|</li>
            <li>
              <Link to="/guides" className="hover:text-wb-amber-700 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-wb-amber-700 p-1">
                {isBn ? 'ক্লিনিক্যাল নির্দেশিকা' : 'Clinical Guides'}
              </Link>
            </li>
            <li aria-hidden="true" className="text-wb-border">|</li>
            <li>
              <Link to="/about" className="hover:text-wb-amber-700 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-wb-amber-700 p-1">
                {isBn ? 'প্রকল্প সম্পর্কে' : 'About Project'}
              </Link>
            </li>
            <li aria-hidden="true" className="text-wb-border">|</li>
            <li>
              <Link to="/about#guidelines" className="hover:text-wb-amber-700 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-wb-amber-700 p-1">
                {isBn ? 'ক্লিনিক্যাল নির্দেশিকা (WHO / ICMR)' : 'Clinical Guidelines'}
              </Link>
            </li>
            <li aria-hidden="true" className="text-wb-border">|</li>
            <li>
              <Link to="/about#disclaimer" className="hover:text-wb-amber-700 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-wb-amber-700 p-1">
                {isBn ? 'আইনি দাবিত্যাগ' : 'Disclaimer'}
              </Link>
            </li>
            <li aria-hidden="true" className="text-wb-border">|</li>
            <li>
              <a
                href="https://wbhealth.gov.in"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-wb-amber-700 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-wb-amber-700 p-1 inline-flex items-center gap-1"
              >
                <span>{isBn ? 'স্বাস্থ্য ভবন পোর্টাল' : 'wbhealth.gov.in'}</span>
                <span className="text-[10px]" aria-hidden="true">↗</span>
              </a>
            </li>
          </ul>
        </nav>

        {/* Statutory Medical Disclaimer */}
        <div className="max-w-4xl text-[11px] leading-relaxed text-wb-text-muted bg-wb-canvas/80 border border-wb-border/80 rounded-lg p-3.5">
          <p className="font-semibold text-wb-text-main mb-1">
            {isBn ? 'চিকিৎসাগত দাবিত্যাগ (Statutory Disclaimer):' : 'Statutory Medical Disclaimer:'}
          </p>
          <p>
            {isBn
              ? 'গার্ডডেঙ্গু কলকাতা বিশ্ববিদ্যালয়ের এ.কে.সি.এস.আই.টি-র একটি গবেষণামূলক স্বাস্থ্য সচেতনতা প্রোটোটাইপ। এটি WHO এবং ICMR নির্দেশিকার ভিত্তিতে তথ্য সরবরাহ করে এবং কোনোভাবেই চিকিৎসাগত নির্ণয় (Diagnosis), ক্লিনিক্যাল ট্রায়াজ, বা প্রেসক্রিপশন প্রদান করে না। কোনো জরুরি শারীরিক পরিস্থিতিতে অবিলম্বে ১০৮/১০২ নম্বরে যোগাযোগ করুন অথবা নিকটবর্তী হাসপাতালে যান।'
              : 'GuardDengue is an academic health-awareness research prototype developed at A.K.C.S.I.T., University of Calcutta, proposed for the Department of Health & Family Welfare, Government of West Bengal. It provides evidence-grounded information from WHO and ICMR guidelines and does NOT provide medical diagnosis, clinical triage, or prescriptions. For medical emergencies, dial 108/102 immediately.'}
          </p>
        </div>

        {/* Academic Credits */}
        <div className="text-[11px] text-wb-text-muted">
          <p>© 2026 Department of Health & Family Welfare, Government of West Bengal</p>
          <p className="font-mono mt-0.5 text-[10px]">
            Academic Prototype • A.K. Choudhury School of Information Technology, University of Calcutta
          </p>
        </div>
      </div>
    </footer>
  )
}
