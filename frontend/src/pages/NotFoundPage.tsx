/**
 * NotFoundPage — Civic 404 Error Page
 */
import { Link } from 'react-router-dom'
import { AlertCircle, Home } from 'lucide-react'
import { useSettings } from '@/store/settings'

export default function NotFoundPage() {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-6 space-y-4">
      <div className="w-16 h-16 rounded-3xl bg-amber-50 text-wb-amber-700 border border-amber-200 flex items-center justify-center shadow-xs">
        <AlertCircle className="w-8 h-8" aria-hidden="true" />
      </div>

      <div className="space-y-1.5 max-w-md">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          404
        </h1>
        <h2 className="text-base sm:text-lg font-bold text-slate-800">
          {isBn ? 'পৃষ্ঠাটি পাওয়া যায়নি' : 'Page Not Found'}
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
          {isBn
            ? 'আপনি যে পৃষ্ঠাটি খুঁজছেন তা স্থানান্তরিত বা মুছে ফেলা হয়েছে।'
            : 'The page you are looking for does not exist or has been moved.'}
        </p>
      </div>

      <div className="pt-2">
        <Link
          to="/"
          className="min-h-[44px] px-5 py-2.5 rounded-xl bg-wb-amber-700 hover:bg-wb-ochre-800 text-white font-semibold text-xs sm:text-sm inline-flex items-center gap-2 shadow-xs transition-colors"
        >
          <Home className="w-4 h-4" aria-hidden="true" />
          <span>{isBn ? 'মূল পাতায় ফিরে যান' : 'Return to Sahayata Desk'}</span>
        </Link>
      </div>
    </div>
  )
}
