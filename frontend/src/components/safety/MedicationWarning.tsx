/**
 * MedicationWarning — NSAID Intercept & Medication Safety Modal (Zone 2)
 *
 * Built on @radix-ui/react-dialog with WAI-ARIA focus trap and keyboard dismissal.
 *
 * Communicates:
 * 1. Strict contraindication of NSAIDs (Ibuprofen, Aspirin, Naproxen, Diclofenac)
 *    during acute dengue fever due to platelet inhibition and gastric bleeding hazard.
 * 2. Crucial nuance for chronic therapies: Do NOT self-discontinue prescribed
 *    cardiovascular aspirin or anticoagulants without immediate clinical consultation.
 * 3. Safe alternative: Paracetamol (Acetaminophen) with conservative dosing rules.
 */
import * as Dialog from '@radix-ui/react-dialog'
import { AlertCircle, Pill, X, ShieldCheck, AlertTriangle } from 'lucide-react'
import { useSettings } from '@/store/settings'

export interface MedicationWarningProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  detectedDrug?: string
}

export default function MedicationWarning({
  open,
  onOpenChange,
  detectedDrug,
}: MedicationWarningProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs transition-opacity animate-in fade-in duration-200" />
        <Dialog.Content
          className="fixed left-1/2 top-1/2 z-50 w-[92vw] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white p-5 sm:p-6 shadow-2xl border-2 border-amber-500 focus:outline-none animate-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto"
          aria-describedby="medication-warning-description"
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-3 pb-3 border-b border-amber-100">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
                <Pill className="w-6 h-6" aria-hidden="true" />
              </div>
              <div>
                <Dialog.Title className="text-base sm:text-lg font-bold text-amber-950 leading-tight">
                  {isBn ? 'ডেঙ্গুতে ওষুধ সুরক্ষা নির্দেশিকা' : 'Dengue Medication Safety Advisory'}
                </Dialog.Title>
                <span className="inline-block mt-0.5 text-[11px] font-semibold text-amber-800 uppercase tracking-wider">
                  {isBn ? 'এনএসএআইডি (NSAID) রক্তক্ষরণ ঝুঁকি' : 'NSAID Bleeding & Platelet Warning'}
                </span>
              </div>
            </div>

            <Dialog.Close
              className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              aria-label={isBn ? 'সতর্কতা বন্ধ করুন' : 'Close medication advisory'}
            >
              <X className="w-5 h-5" aria-hidden="true" />
            </Dialog.Close>
          </div>

          {/* Content */}
          <div id="medication-warning-description" className="py-4 space-y-3.5 text-xs sm:text-sm text-slate-700 leading-relaxed">
            {detectedDrug && (
              <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 font-medium">
                <strong>{isBn ? 'চিহ্নিত ওষুধ: ' : 'Inquired Medication: '}</strong>
                {detectedDrug}
              </div>
            )}

            {/* Red Alert: Contraindicated Drugs */}
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 space-y-1 text-xs">
              <div className="flex items-center gap-1.5 font-bold text-red-900">
                <AlertCircle className="w-4 h-4 text-red-600 shrink-0" aria-hidden="true" />
                <span>{isBn ? 'কখনই গ্রহণ করবেন না (Contraindicated):' : 'Strictly Avoid for Fever:'}</span>
              </div>
              <p className="text-red-800">
                {isBn
                  ? 'আইবুপ্রোফেন (Ibuprofen), অ্যাসপিরিন (Aspirin), মেফেনামিক অ্যাসিড, ডাইক্লোফেনাক বা যেকোনো ব্যথানাশক। এগুলি রক্ত জমাট বাঁধার ক্ষমতা কমায় এবং পাকস্থলীতে প্রাণঘাতী রক্তক্ষরণ ঘটাতে পারে।'
                  : 'Ibuprofen, Aspirin, Mefenamic Acid, Diclofenac, Naproxen, or any other NSAID. These impair platelet function and trigger catastrophic gastrointestinal hemorrhages.'}
              </p>
            </div>

            {/* Prescribed Chronic Medication Warning */}
            <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 space-y-1 text-xs">
              <div className="flex items-center gap-1.5 font-bold text-amber-900">
                <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0" aria-hidden="true" />
                <span>{isBn ? 'নিয়মিত প্রেসক্রিপশনযুক্ত ওষুধ বন্ধ করবেন না:' : 'Important Chronic Prescription Notice:'}</span>
              </div>
              <p className="text-amber-800">
                {isBn
                  ? 'যদি আপনি হার্টের সুরক্ষায় বা অন্যান্য ক্রনিক রোগের কারণে আগে থেকেই অ্যাসপিরিন বা রক্ত পাতলা করার ওষুধ খাচ্ছেন, তবে নিজে নিজে তা বন্ধ করবেন না। অবিলম্বে আপনার চিকিৎসকের পরামর্শ নিন।'
                  : 'If you take low-dose aspirin or anticoagulants prescribed for existing cardiovascular conditions, DO NOT stop them on your own. Consult your treating doctor immediately.'}
              </p>
            </div>

            {/* Safe Alternative: Paracetamol */}
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 space-y-1 text-xs">
              <div className="flex items-center gap-1.5 font-bold text-emerald-900">
                <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" aria-hidden="true" />
                <span>{isBn ? 'অনুমোদিত নিরাপদ জ্বর নিয়ন্ত্রণ:' : 'Safe Alternative: Paracetamol (Acetaminophen)'}</span>
              </div>
              <p className="text-emerald-800">
                {isBn
                  ? 'কেবলমাত্র প্যারাসিটামল ব্যবহার করা যেতে পারে (বড়দের ক্ষেত্রে প্রতি ডোজে ৫০০-৬৫০ মিলিগ্রাম, দিনে সর্বোচ্চ ৩-৪ বার, কমপক্ষে ৪-৬ ঘণ্টার ব্যবধানে)। চিকিৎসকের পরামর্শ ছাড়া অতিরিক্ত মাত্রা ক্ষতিকর।'
                  : 'Paracetamol alone is recommended for fever (500–650mg per dose for adults, maximum 3–4 times daily, separated by at least 4–6 hours). Never exceed recommended daily ceilings.'}
              </p>
            </div>
          </div>

          {/* Footer Action */}
          <div className="pt-3 border-t border-slate-100 flex justify-end">
            <Dialog.Close asChild>
              <button
                type="button"
                className="min-h-[44px] px-5 py-2 rounded-xl bg-wb-amber-700 hover:bg-wb-ochre-800 text-white font-semibold text-xs sm:text-sm cursor-pointer transition-all shadow-xs"
              >
                {isBn ? 'আমি বুঝেছি / ঠিক আছে' : 'I Understand'}
              </button>
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
