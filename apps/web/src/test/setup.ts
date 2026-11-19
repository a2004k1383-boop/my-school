import { config } from '@vue/test-utils'

config.global.stubs = {}
document.documentElement.setAttribute('lang', 'fa')
document.documentElement.setAttribute('dir', 'rtl')
