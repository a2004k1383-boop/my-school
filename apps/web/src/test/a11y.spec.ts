import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('@/modules/auth/api', () => ({
  loginUser: vi.fn(),
  registerUser: vi.fn(),
  logoutUser: vi.fn(),
  currentUser: vi.fn(),
  refreshAccessToken: vi.fn().mockResolvedValue(false),
}))

import LoginView from '@/modules/auth/views/LoginView.vue'
import RegisterView from '@/modules/auth/views/RegisterView.vue'

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', name: 'login', component: { template: '<div />' } },
      { path: '/register', name: 'register', component: { template: '<div />' } },
    ],
  })
}

async function mountView(component: typeof LoginView, path: string) {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = makeRouter()
  await router.push(path)
  await router.isReady()
  return mount(component as never, { global: { plugins: [pinia, router] } })
}

describe('accessibility smoke', () => {
  it('labels every input on the login page', async () => {
    const wrapper = await mountView(LoginView, '/login')

    for (const input of wrapper.findAll('input')) {
      const id = input.attributes('id')
      if (id === undefined) {
        continue
      }
      expect(wrapper.find(`label[for="${id}"]`).exists()).toBe(true)
    }
    expect(wrapper.find('h1').text()).toBeTruthy()
  })

  it('groups role choices with a legend and labels every input', async () => {
    const wrapper = await mountView(RegisterView, '/register')

    expect(wrapper.find('fieldset legend').text()).toBeTruthy()
    for (const input of wrapper.findAll('input')) {
      const id = input.attributes('id')
      if (id !== undefined) {
        expect(wrapper.find(`label[for="${id}"]`).exists()).toBe(true)
      }
    }
  })
})
