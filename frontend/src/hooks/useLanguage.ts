/** useLanguage hook stub — TODO: Implement */
import { useSettings } from '@/store/settings'
import { TOPIC_LABELS } from '@/constants'
import type { KnowledgeTopic } from '@/types'

export function useLanguage() {
  const { settings, setLanguage } = useSettings()
  const t = (topic: KnowledgeTopic) => TOPIC_LABELS[topic][settings.language]
  return { language: settings.language, setLanguage, t }
}
