/**
 * EmergencyDialog — High-Urgency Hospital Referral Modal (Zone 2 Safety)
 *
 * Built on @radix-ui/react-dialog for 100% WAI-ARIA compliance, focus trapping,
 * and keyboard Escape dismissal.
 *
 * Triggered when critical dengue warning signs occur (severe abdominal pain,
 * persistent vomiting, mucosal bleeding, fluid accumulation, lethal defervescence).
 *
 * Implements one-tap click-to-dial for 108 (State Ambulance) and 102.
 */
import * as Dialog from '@radix-ui/react-dialog'
import { AlertTriangle, PhoneCall, X, ShieldAlert, ArrowRight } from 'lucide-react'
import { useSettings } from '@/store/settings'

export interface EmergencyDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  symptomSummary?: string
}

export default function EmergencyDialog({
  open,
  onOpenChange,
  symptomSummary,
}: EmergencyDialogProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs transition-opacity animate-in fade-in duration-200" />
        <Dialog.Content
          className="fixed left-1/2 top-1/2 z-50 w-[92vw] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white p-5 sm:p-6 shadow-2xl border-2 border-red-500 focus:outline-none animate-in zoom-in-95 duration-200"
          aria-describedby="emergency-dialog-description"
        >
          {/* Header Banner */}
          <div className="flex items-start justify-between gap-3 pb-3 border-b border-red-100">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-red-100 text-red-700 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-6 h-6 animate-pulse" aria-hidden="true" />
              </div>
              <div>
                <Dialog.Title className="text-base sm:text-lg font-bold text-red-950 leading-tight">
                  {isBn ? 'জরুরী সতর্কতা — অবিলম্বে হাসপাতালে যান' : 'Emergency Referral — Hospitalize Immediately'}
                </Dialog.Title>
                <span className="inline-block mt-0.5 text-[11px] font-semibold text-red-700 uppercase tracking-wider">
                  {isBn ? 'ডেঙ্গু সংকটপূর্ণ পর্যায় (দিন ৩–৭)' : 'Critical Phase Warning (Days 3–7)'}
                </span>
              </div>
            </div>

            <Dialog.Close
              className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
              aria-label={isBn ? 'সতর্কতা বন্ধ করুন' : 'Close warning dialog'}
            >
              <X className="w-5 h-5" aria-hidden="true" />
            </Dialog.Close>
          </div>

          {/* Dialog Description & Advisory */}
          <div id="emergency-dialog-description" className="py-4 space-y-3 text-xs sm:text-sm text-slate-700 leading-relaxed">
            {symptomSummary && (
              <div className="p-2.5 rounded-lg bg-red-50 border border-red-200 text-red-900 font-medium">
                <strong>{isBn ? 'চিহ্নিত বিপদ সংকেত: ' : 'Detected Warning Sign: '}</strong>
                {symptomSummary}
              </div>
            )}

            <p>
              {isBn
                ? 'ডেঙ্গু জ্বরে তাপমাত্রা কমার সময় (দিন ৩ থেকে ৭) প্লাজমা লিকেজের কারণে রক্তচাপ কমে ডেঙ্গু শক সিন্ড্রোম দেখা দিতে পারে। এই সময় বাড়িতে অপেক্ষা করা প্রাণঘাতী হতে পারে।'
                : 'When high fever subsides (Days 3–7), capillary permeability can cause plasma leakage and rapid progression to Dengue Shock Syndrome. Waiting at home during this phase is dangerous.'}
            </p>

            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1.5 text-xs">
              <div className="flex items-center gap-1.5 font-bold text-slate-900">
                <ShieldAlert className="w-4 h-4 text-red-600 shrink-0" aria-hidden="true" />
                <span>{isBn ? 'অবিলম্বে যা করণীয়:' : 'Immediate Actions Required:'}</span>
              </div>
              <ul className="list-disc list-inside space-y-1 text-slate-700 pl-1">
                <li>{isBn ? 'নিকটবর্তী সরকারি বা বেসরকারি হাসপাতালের জরুরী বিভাগে যান' : 'Go directly to the nearest hospital Emergency Department'}</li>
                <li>{isBn ? 'রোগীকে একটানা শুইয়ে রাখুন ও পর্যাপ্ত ওআরএস/তরল দিন (যদি বমি না থাকে)' : 'Keep the patient supine and hydrated (if no recurrent vomiting)'}</li>
                <li>{isBn ? 'কোনো ব্যথানাশক (আইবুপ্রোফেন/অ্যাসপিরিন) দেবেন না' : 'Do NOT administer NSAIDs (Ibuprofen, Aspirin, Diclofenac)'}</li>
              </ul>
            </div>
          </div>

          {/* Action Dialers */}
          <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
            <a
              href="tel:108"
              className="min-h-[48px] px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all cursor-pointer text-sm"
            >
              <PhoneCall className="w-4 h-4 animate-bounce" aria-hidden="true" />
              <span>{isBn ? '১০৮ নম্বরে অ্যাম্বুলেন্স ডাকুন' : 'Call 108 Ambulance (Free)'}</span>
            </a>

            <a
              href="tel:1800313444222"
              className="min-h-[44px] px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer text-xs"
            >
              <span>{isBn ? 'স্বাস্থ্য ভবন হেল্পলাইন' : 'WB Health Helpline'}</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-600" aria-hidden="true" />
            </a>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
