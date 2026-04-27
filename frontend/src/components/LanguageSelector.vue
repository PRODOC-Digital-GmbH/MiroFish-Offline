<template>
  <select
    :value="locale"
    class="language-selector"
    @change="changeLocale($event.target.value)"
  >
    <option v-for="lang in locales" :key="lang.code" :value="lang.code">
      {{ lang.label }}
    </option>
  </select>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { SUPPORTED_LOCALES } from '../i18n'

const { locale } = useI18n()
const locales = SUPPORTED_LOCALES

function changeLocale(code) {
  locale.value = code
  localStorage.setItem('simulab-locale', code)
}
</script>

<style scoped>
.language-selector {
  appearance: none;
  background: transparent;
  border: 1px solid #E0E0E0;
  padding: 4px 24px 4px 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23666'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.language-selector:hover {
  border-color: #999;
}

.language-selector:focus {
  outline: none;
  border-color: #FF4500;
}
</style>
