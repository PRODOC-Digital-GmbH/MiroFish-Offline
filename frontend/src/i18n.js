import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import de from './locales/de.json'

export const SUPPORTED_LOCALES = [
  { code: 'en', label: 'English' },
  { code: 'de', label: 'Deutsch' }
]

function getInitialLocale() {
  const stored = localStorage.getItem('simulab-locale')
  if (stored && SUPPORTED_LOCALES.some(l => l.code === stored)) return stored

  const browserLang = navigator.language?.split('-')[0]
  if (SUPPORTED_LOCALES.some(l => l.code === browserLang)) return browserLang

  return 'en'
}

const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(),
  fallbackLocale: 'en',
  flatJson: true,
  messages: { en, de }
})

export default i18n
